import express from "express";
import { config } from "dotenv";
import bodyParser from 'body-parser';
import bodyParserXml from 'body-parser-xml';
import { sendDifyMessage } from './difynodes.js'; // 确保路径正确
import { Message } from "./message.js";
import { initAccessToken } from "./config.js";

config({ path: '.env.local' });
bodyParserXml(bodyParser);

const app = express();
const PORT = process.env.PORT || 6060;
const message = new Message();

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(bodyParser.xml());

app.get('/healthz', function (req, res, next) {
    res.status(200).end();
});

app.get('/message', function (req, res, next) {
    message.urlSetting(req, res);
});

app.post('/message', function (req, res, next) {
    message.getMsgObj(req).then(result => {
        const question = result?.Content[0];
        console.log(question);
        const toUser = result.FromUserName[0];

        // 先发送一个临时回复
        message.reply(res, { type: 'text', content: '容朕三思...' }, toUser);

        // 使用新的 AI 聊天功能获取回复
        sendDifyMessage(question, toUser, (reply) => {
            // 将 AI 的回复发送给用户
            message.sendMsg(reply, toUser);
        }).catch(error => {
            console.error('Error during AI chat:', error);
        });
    }).catch(error => {
        console.error('Error handling message object:', error);
    });
});

initAccessToken();

app.listen(PORT, () => {
    console.log(`Server Running on Port:${PORT}`);
});