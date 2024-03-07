import axios from 'axios';

// 假设 Flask 应用的 URL 是 http://localhost:5000/chat
const FLASK_CHAT_URL = 'http://localhost:5000/chat';

// 发送用户输入到 Flask 应用并获取 AI 的回应
const getAIChat = async (userInput) => {
    try {
        const response = await axios.post(FLASK_CHAT_URL, {
            user_input: userInput
        });
        console.log(response.data); // 修正这里
        return response.data;
    } catch (error) {
        console.error('Error fetching AI response:', error);
        return null;
    }
};

export default getAIChat;
