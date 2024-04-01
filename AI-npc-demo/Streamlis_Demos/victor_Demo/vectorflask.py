import datetime
import json
import os
import sys
from flask import Flask, request, jsonify

import openai
# 获取 utils.py 所在的文件夹路径
utils_path = os.path.abspath('/home/ubuntu/WeWork-OpenAI-Node/AI-npc-demo/Streamlis_Demos/Utils')

# 将 utils.py 所在的文件夹添加到 sys.path
if utils_path not in sys.path:
    sys.path.append(utils_path)

from utils import AI_Response_API  # 确保这里是你的 MY_SQL_API 类
# 获取 utils.py 所在的文件夹路径
utils_path = os.path.abspath('/home/ubuntu/WeWork-OpenAI-Node/AI-npc-demo/Streamlis_Demos/Utils/MySql_Utils')

# 将 utils.py 所在的文件夹添加到 sys.path
if utils_path not in sys.path:
    sys.path.append(utils_path)

from mysql_api import MY_SQL_API  # 确保这里是你的 MY_SQL_API 类

# 获取 utils.py 所在的文件夹路径
utils_path = os.path.abspath('/home/ubuntu/WeWork-OpenAI-Node/AI-npc-demo/Streamlis_Demos/Utils/GPT_Utils')

# 将 utils.py 所在的文件夹添加到 sys.path
if utils_path not in sys.path:
    sys.path.append(utils_path)

from gpt_api import *  


# 配置MySQL 连接信息
MYSQL_HOST = "localhost"  # 或者是远程服务器的IP地址/域名
MYSQL_USER = "lele"  # 你的 MySQL 用户名
MYSQL_PASSWORD = "Ogcloud123"  # 你的 MySQL 密码
MYSQL_DATABASE = "gptchat"  # 你想要连接的数据库名称


# 初始化 MySQL 连接
db = MY_SQL_API(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)

ai_res = AI_Response_API()

# 创建一个数据库表（如果不存在）
def create_table():
    create_table_query1 = """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_input TEXT,
            gpt_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """
    create_table_query2 = """
        CREATE TABLE IF NOT EXISTS token_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            input_tokens INT,
            prompt_tokens  INT,
            aires_tokens INT,
            STM_tokens   INT,
            vector_tokens INT,
            total_tokens  INT
        )
    """
    db.execute_query(create_table_query1)
    
    db.execute_query(create_table_query2)

# create_table()

# 保存聊天记录到数据库
def save_chat_to_db(user_input, gpt_response):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    insert_query = """
        INSERT INTO chat_history (user_input, gpt_response, timestamp)
        VALUES (%s, %s, %s)
    """
    db.execute_query(insert_query, (user_input, gpt_response, timestamp))
    
# 从数据库获取聊天历史
def get_chat_history():
    select_query = "SELECT user_input, gpt_response, timestamp FROM chat_history"
    try:
        results = db.select(select_query)
        return results if results is not None else []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
# 从数据库中获取 token开销
def get_token_data():
    select_query = "SELECT input_tokens,prompt_tokens,aires_tokens,STM_tokens,vector_tokens,total_tokens FROM token_history"
    try:
        results = db.select(select_query)
        return results if results is not None else []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
# 使用 GPT-3 生成回复
def get_gpt_response(prompt):
    # 获取并流式显示AI响应
    ai_response = ai_res.stream_get_response(systemset="你需要和用户对话，尽可能回答用户问题", prompt=prompt)
    return ai_response



ai_res = AI_Response_API()


# 定义一个函数来处理 datetime 对象，使其可被 JSON 序列化
def json_serializable(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")


# 从数据库获取聊天历史并保存到 JSON 文件
def save_chat_history_from_db_to_json(file_path='chat_history.json'):
    new_chat_history = []
    try:
        chat_history_tuples = get_chat_history()
        # 将元组转换为字典列表
        new_chat_history = [
            {
                'user_input': record[0],
                'gpt_response': record[1],
                'timestamp': str(record[2])
            }
            for record in chat_history_tuples
        ]
    except Exception as e:
        print("error")
        return

    try:
        # 如果文件存在，读取旧聊天历史
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as json_file:
                existing_chat_history = json.load(json_file)
        else:
            existing_chat_history = []
            
        
        # 将新数据追加到旧数据中
        combined_chat_history  = existing_chat_history + new_chat_history

        # 根据时间戳排序聊天历史 (降序，即最新的记录在前)
        sorted_chat_history = sorted(combined_chat_history, key=lambda x: x['timestamp'], reverse=True)
        
        # 保存更新后的聊天历史到 JSON 文件
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(sorted_chat_history, json_file, default=json_serializable, ensure_ascii=False, indent=4)
    except Exception as e:
        print("error")
def get_chat_history_as_string():
    # 获取聊天历史记录，假设它是一个列表，每个元素包含(user_input, gpt_response, timestamp)
    chat_history = get_chat_history()
    # 初始化short_history为空字符串
    short_history = ""
    # 遍历聊天历史记录，将每条记录格式化后添加到short_history字符串中
    for user_input, gpt_response, timestamp in chat_history:
        # 将每条记录格式化后添加到short_history字符串中
        short_history += f"User: {user_input}\nGPT: {gpt_response}\nTime: {timestamp}\n\n"
    # 返回格式化后的聊天历史字符串
    return short_history
       

# 创建 Flask 应用
app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('user_input')
    if not user_input:
        return jsonify({'error': 'No user input provided'}), 400
    
    shorthistory = get_chat_history_as_string()
    tokens_limit = token_compute(shorthistory)
    
    if tokens_limit>1000:
        # 1、保存----你可以在合适的地方调用这个函数，例如在会话结束时或定期保存聊天记录
        save_chat_history_from_db_to_json()
        # 2、删除chat_history数据库中的短期数据
        delete_query = "DELETE FROM chat_history"
        db.execute_query(delete_query)
        # 2、删除token_history数据库中的短期数据
        delete_query = "DELETE FROM token_history"
        db.execute_query(delete_query)
       
    if user_input:
        #向量数据获取
        # 创建AI_Response_API的实例
        aires = AI_Response_API()
        path = "/home/ubuntu/WeWork-OpenAI-Node/AI-npc-demo/Streamlis_Demos/victor_Demo/test/dialog"
        info=aires.vector_file(input=user_input,path=path )
        
        path2 = "/home/ubuntu/WeWork-OpenAI-Node/AI-npc-demo/Streamlis_Demos/victor_Demo/test/src"
        info2=aires.vector_file(input=user_input,path =path2 )
        print("------------------------------------",user_input)
        #总prompt 
        total_prompt = f"""
            下面是对话的历史记录
            {shorthistory}
            
            下面是与用户输入相关的额外提示
            {str(info)}
            下面是额外的资料
            {info2}
            你需要根据上面我给出的提示和用户对话，尽可能回答用户问题
        """
        # print(total_prompt)
        # 获取并流式显示AI响应
        ai_response = ai_res.get_response(
            systemset=total_prompt, 
            prompt=user_input,
            stream=False
            )
        print("------------------------------------",str(ai_response))
        # 保存聊天记录到数据库
        save_chat_to_db(user_input, ai_response)

    
    # 返回 AI 的响应
    return jsonify({'ai_response': ai_response})
    
 # 启动 Flask 应用
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)       
