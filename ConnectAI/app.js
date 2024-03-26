import express from "express";
import { config } from "dotenv";
import bodyParser from 'body-parser';
import bodyParserXml from 'body-parser-xml';

import getAIChat from "./openai.js";
import { Message } from "./message.js";
import { initAccessToken } from "./config.js";

config({ path: '.env.local' });
bodyParserXml(bodyParser);

const app = express();
const PORT = process.env.PORT;
const message = new Message();

/*message.log();*/

/*config parser for body*/
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(bodyParser.xml());

/*health check for render*/
app.get('/healthz', function (req, res, next) {
    res.status(200).end();
});

/*receive server url setting*/
app.get('/message', function (req, res, next) {
    message.urlSetting(req, res);
});

/*passive message response*/
app.post('/message', function (req, res, next) {
    // 获取消息对象
    message.getMsgObj(req).then(result => {
        const question = result?.Content[0];
        console.log(question);
        const toUser = result.FromUserName[0];

        // 先发送一个临时回复
        message.reply(res, { type: 'text', content: '容朕三思...' }, toUser);

        // 使用 AI 聊天功能获取回复
        getAIChat(question).then(aiResponse => {
            // 假设 aiResponse 包含 ai_response 字段
            const content = aiResponse?.ai_response;
            if (content) {
                // 将 AI 的回复发送给用户
                message.sendMsg(content, toUser);
            }
        }).catch(error => {
            console.error('Error during AI chat:', error);
        });
    }).catch(error => {
        console.error('Error handling message object:', error);
    });
});


/*init access_token*/
initAccessToken();

app.listen(PORT, () => {
    console.log(`Server Running on Port:${PORT}`);
});