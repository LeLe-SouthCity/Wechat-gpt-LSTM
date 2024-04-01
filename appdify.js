import express from "express";
import { config } from "dotenv";
import bodyParser from 'body-parser';
import bodyParserXml from 'body-parser-xml';
import { sendDifyMessage } from './difynodes.js'; // 确保路径正确
import { Message } from "./message.js";
import { initAccessToken } from "./config.js";
import redis from 'redis';

config({ path: '.env.local' });
bodyParserXml(bodyParser);

const app = express();
const PORT = process.env.PORT;
const message = new Message();

// 创建Redis客户端
const redisClient = redis.createClient({
  url: process.env.REDIS_URL // Redis服务器URL
});

// 连接到Redis服务器
redisClient.connect();

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(bodyParser.xml());

app.get('/healthz', function (req, res, next) {
    res.status(200).end();
});

app.get('/message', function (req, res, next) {
    message.urlSetting(req, res);
});

// /message路由
app.post('/message', function (req, res, next) {
  message.getMsgObj(req).then(async result => {
    const question = result?.Content[0];
    console.log(question);
    const toUser = result.FromUserName[0];

    // 先发送一个临时回复
    message.reply(res, { type: 'text', content: '容朕三思...' }, toUser);
      
    try {
      // 尝试从Redis获取历史conversation_id
      const historyId = await redisClient.get(toUser);

      // 使用新的 AI 聊天功能获取回复
      const { answer, conversation_id } = await sendDifyMessage(question, toUser, historyId);

      // 将 AI 的回复（仅answer字段的内容）发送给用户
      if (answer) {
        // 将 AI 的回复发送给用户
        message.sendMsg(answer, toUser);
      }
      
      // 保存新的conversation_id到Redis
      if (conversation_id) {
        await redisClient.set(toUser, conversation_id);
      }
    } catch (error) {
      console.error('Error during AI chat:', error);
      // 错误处理逻辑
    }
  }).catch(error => {
    console.error('Error handling message object:', error);
    // 错误处理逻辑
  });
});

initAccessToken();

app.listen(PORT, () => {
    console.log(`Server Running on Port:${PORT}`);
});
