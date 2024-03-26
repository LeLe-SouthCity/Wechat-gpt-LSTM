import cloud from '@lafjs/cloud'
import { decrypt, getSignature } from '@wecom/crypto'
import xml2js from 'xml2js'
function genConversationKey(userName) {
  return `${process.env.WXWORK_AGENTID}:${userName}`
}

function genWxAppAccessTokenKey() {
  return `${process.env.WXWORK_AGENTID}:access-token`
}

async function getToken() {
  console.log('[getToken] called')

  const cache = cloud.shared.get(genWxAppAccessTokenKey())
  if (cache && cache.expires >= Date.now()) return cache.token

  const res = await cloud.fetch({
    url: 'https://qyapi.weixin.qq.com/cgi-bin/gettoken',
    method: 'GET',
    params: {
      corpid: process.env.WXWORK_CORPID,
      corpsecret: process.env.WXWORK_CORPSECRET,
    }
  })

  const token = res.data.access_token
  cloud.shared.set(genWxAppAccessTokenKey(), { token, expires: Date.now() + res.data.expires_in * 1000 })
  return token
}

async function sendWxMessage(message, user) {
  console.log('[sendWxMessage] called', user, message)

  const res = await cloud.fetch({
    url: 'https://qyapi.weixin.qq.com/cgi-bin/message/send',
    method: 'POST',
    params: {
      access_token: await getToken()
    },
    data: {
      "touser": user,
      "msgtype": "text",
      "agentid": process.env.WXWORK_AGENTID,
      "text": {
        "content": message
      },
      "safe": 0,
      "enable_id_trans": 0,
      "enable_duplicate_check": 0,
      "duplicate_check_interval": 1800
    },
  })
  console.log('[sendWxMessage] received', res.data)
}

// async function sendDifyMessage(message, userName, onMessage) {
//   console.log('[sendDifyMessage] called', message, userName)

//   const conversationId = cloud.shared.get(genConversationKey(userName)) || null
//   let newConversationId = ''
//   let responseText = ''

//   try {
//     const response = await cloud.fetch({
//       url: 'http://10.50.146.102/v1/chat-messages',
//       method: 'POST',
//       headers: {
//         'Authorization': `Bearer app-QUUb1aNeslCUaPF1zsLynjqr`
//       },
//       data: {
//         inputs: {},
//         response_mode: "streaming",
//         query: message,
//         user: userName,
//         conversation_id: conversationId
//       },
//       responseType: "stream"
//     })

//     let firstHalfMessage = ''
//     response.data.on('data', (data) => {
//       let message = data.toString()
//       try {
//         if (firstHalfMessage) {
//           message += firstHalfMessage
//           firstHalfMessage = ''
//         }

//         // 检查是不是sse协议
//         if (!message.startsWith('data: ')) return

//         const parsedChunk= JSON.parse(message.substring(6))

//         if (!newConversationId) {
//           newConversationId = parsedChunk.conversation_id
//           cloud.shared.set(genConversationKey(userName), newConversationId)
//         }
//         const { answer } = parsedChunk
//         responseText += answer

//         // 伪流式响应
//         if (answer.endsWith('\n\n') || (responseText.length > 120 && /[?。；！]$/.test(responseText))) {
//           onMessage(responseText.replace('\n\n', ''))
//           console.log('[sendDifyMessage] received', responseText, newConversationId)
//           responseText = ''
//         }
//       } catch (e) {
//         firstHalfMessage = message
//         console.error('[sendDifyMessage] error', message)
//       }

//     })

//     // stream结束时把剩下的消息全部发出去
//     response.data.on('end', () => {
//       onMessage(responseText.replace('\n\n', ''))
//     })
//   } catch (e) {
//     console.error("[sendDifyMessage] error", e)
//   }
// }

// difynodes.js
import axios from 'axios';

const sendDifyMessage = async (query, user) => {
  const url = 'http://10.50.146.102/v1/chat-messages';
  const headers = {
      'Authorization': 'Bearer app-QUUb1aNeslCUaPF1zsLynjqr',
      'Content-Type': 'application/json'
  };
  const data = {
      "inputs": {},
      "query": query,
      "response_mode": "blocking",
      "user": user,
  };

  try {
    const response = await axios.post(url, data, { headers: headers });
    const answer = response.data.answer;
    if (answer) { // 检查是否有输出
      console.log('已输出:', answer); // 在日志中记录输出
    }
    return answer; // 仅返回answer字段
  } catch (error) {
    console.error(error);
    throw error; // 抛出异常以便调用者处理
  }
};


export { sendDifyMessage };



async function asyncSendMessage(xml) {
  console.log('[asyncSendMessage] called', xml)

  if (xml.MsgType[0] !== 'text') return

  const message = xml.Content[0]
  const userName = xml.FromUserName[0]

  if (message === '/new') {
    // 重置conversation id
    cloud.shared.set(genConversationKey(userName), null)
    sendWxMessage('新建成功，开始新的对话吧~~', userName)
    return
  }

  sendWxMessage('AI思考中, 请耐心等待~~', userName)

  try {
    sendDifyMessage(message, userName, (message) => {
      sendWxMessage(message, userName)
    })
  }
  catch (e) {
    console.error('[sendDifyMessage] error', e)
    sendWxMessage('接口请求失败，请联系管理员查看错误信息', userName)
  }
}

export default async function (ctx) {
  if (!ctx || !ctx.request) {
    console.error('ctx or ctx.request is undefined');
    return { message: '内部服务器错误', code: 500 };
  }
  const { query } = ctx
  const { msg_signature, timestamp, nonce, echostr } = query
  const token = process.env.WXWORK_TOKEN
  const key = process.env.WXWORK_AESKEY
  console.log('[main] called', ctx.method, ctx.request.url)

  // 签名验证专用
  if (ctx.method === 'GET') {
    const signature = getSignature(token, timestamp, nonce, echostr)
    if (signature !== msg_signature) {
      return { message: '签名验证失败', code: 401 }
    }
    const { message } = decrypt(key, echostr)
    return message
  }

  const payload = ctx.body.xml
  if (!payload || !payload.encrypt || !Array.isArray(payload.encrypt) || payload.encrypt.length === 0) {
    console.error('无效的加密数据');
    return { message: '无效的请求体', code: 400 };
  }
  const encrypt = payload.encrypt[0];
  const signature = getSignature(token, timestamp, nonce, encrypt)
  if (signature !== msg_signature) {
    return { message: '签名验证失败', code: 401 }
  }

  const { message } = decrypt(key, encrypt)
  const {xml} = await xml2js.parseStringPromise(message)
  // 由于GPT API耗时较久，这里提前返回，防止企业微信超时重试，后续再手动调用发消息接口
  // ctx.response.sendStatus(200)

  await asyncSendMessage(xml)

  return { message: true, code: 0 }
}

