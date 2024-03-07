
from flask import Flask, request, jsonify
import os
from openai import OpenAI

# 假设您的 API 密钥存储在环境变量中，名称为 OPENAI_API_KEY
# api_key="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"
# if api_key is None:
#     raise ValueError("No API key provided. Set the OPENAI_API_KEY environment variable.")

client = OpenAI(api_key="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")

app = Flask(__name__)

# 用于处理聊天消息的路由
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('user_input')

    # 调用 OpenAI API 获取聊天机器人的回复
    completion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:ogcloudgpt::8zg4QWKu",
        messages=[
            # 注意,微调模型的微调训练数据中的system role和使用微调模型时的system role应该一致
            {"role": "system", "content": "Og娘是OgCLoud公司的客服聊天机器人"},
            {"role": "user", "content": user_input}
        ]
    )

    # 从响应中提取聊天机器人的消息
    bot_message = completion.choices[0].message.content

    # 返回 AI 的响应
    return jsonify({'ai_response': bot_message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # 启动 Flask 应用
