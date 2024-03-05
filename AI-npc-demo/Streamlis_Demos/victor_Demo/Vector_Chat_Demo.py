import datetime
import json
import os
import sys
import streamlit as st

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


# 和 MySQL 连接信息
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

create_table()

# 保存聊天记录到数据库
def save_chat_to_db(user_input, gpt_response):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    insert_query = """
        INSERT INTO chat_history (user_input, gpt_response, timestamp)
        VALUES (%s, %s, %s)
    """
    db.execute_query(insert_query, (user_input, gpt_response, timestamp))
    
# 保存聊天记录的token到数据库
def save_tokens_to_db(input_tokens,prompt_tokens,aires_tokens,STM_tokens,vector_tokens,total_tokens):
    """
    # 用户输入token
    input_tokens = token_compute(st.session_state['user_input'])
    # 总prompt tokens
    prompt_tokens = token_compute(st.session_state['total_prompt'])
    # aires_tokens tokens
    aires_tokens = token_compute(ai_response)
    #短期记忆 tokens
    STM_tokens = token_compute(st.session_state['short_history'])
    #向量记忆 tokens
    vector_tokens = token_compute(st.session_state['LTM_Vector_get'])
    #总token开销
    total_tokens = prompt_tokens+input_tokens
    """
    insert_query = """
        INSERT INTO token_history (input_tokens, prompt_tokens,aires_tokens, STM_tokens, vector_tokens, total_tokens)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    db.execute_query(insert_query, (input_tokens,prompt_tokens,aires_tokens,STM_tokens,vector_tokens,total_tokens))
    
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




# 初始化会话状态
if 'gpt_chat_history' not in st.session_state:
    st.session_state['gpt_chat_history'] = []
# token计算
if 'tokens_compute' not in st.session_state:
    st.session_state['tokens_compute'] = 0
# 短期记忆记录
if 'short_history' not in st.session_state:
    st.session_state['short_history'] = []
# 短期token限制记录
if 'STM_tokens_limit' not in st.session_state:
    st.session_state['STM_tokens_limit'] = 1000
# 用户输入记录
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = None
#长期记忆向量获取
if 'LTM_Vector_get' not in st.session_state:
    st.session_state['LTM_Vector_get'] = None
#总prompt计算
if 'total_prompt' not in st.session_state:
    st.session_state['total_prompt'] = None
# 初始化会话状态
if 'stream_chat_history' not in st.session_state:
    st.session_state['stream_chat_history'] = []
# 保存token历史
if 'token_history' not in st.session_state:
    st.session_state['token_history'] = get_token_data()

# 保存token历史
if 'LTM_Vector_get_all' not in st.session_state:
    st.session_state['LTM_Vector_get_all'] = get_token_data()


ai_res = AI_Response_API()
# 显示聊天历史
def display_history():
    for message in st.session_state['stream_chat_history']:
        with st.chat_message(message["label"]):
            st.markdown(message["message"])
       
# 处理用户输入和AI响应
def handle_chat(user_input,Ai_res):
    # 将用户输入添加到历史记录中并显示
    st.session_state['stream_chat_history'].append({'label': 'user', 'message': user_input})
    
    st.session_state['stream_chat_history'].append({'label': 'AI', 'message': Ai_res})
    display_history()


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
        # st.info(new_chat_history)
    except Exception as e:
        st.error(f"mysql对话历史记录获取失败: {e}")
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
        st.error(f"An error occurred while saving to JSON: {e}")

def show_STM():
    # 侧边栏显示聊天历史
    with st.sidebar:
        chat_history = get_chat_history()
        for user_input, gpt_response, timestamp in chat_history:
            
            st.session_state['gpt_chat_history'].append(user_input)
            st.session_state['gpt_chat_history'].append(gpt_response)
            # 短期记忆 添加
            st.session_state['short_history'].append(f"User: {user_input}\nGPT: {gpt_response}\nTime: {timestamp}")
        st.write(chat_history)    
# Streamlit 应用
def main():
    

    st.title("Chat with GPT")
    # 使用 number_input 获取整数输入，并设置默认值为 1000
    tokens_limit = st.sidebar.number_input("短期 token 上限", min_value=1, value=st.session_state['STM_tokens_limit'], step=1)
    # 避免切页失去数据
    if tokens_limit!=st.session_state['STM_tokens_limit']:
        st.session_state['STM_tokens_limit'] = tokens_limit
        
    if st.session_state['gpt_chat_history']:
        # 计算 tokens
        st.session_state['tokens_compute'] = token_compute(st.session_state['short_history'])

    
            

    # 聊天界面
    user_input = st.chat_input("Say something to GPT:")
    if st.session_state['tokens_compute']>tokens_limit:
        
        # 1、保存----你可以在合适的地方调用这个函数，例如在会话结束时或定期保存聊天记录
        save_chat_history_from_db_to_json()
        # 2、删除chat_history数据库中的短期数据
        delete_query = "DELETE FROM chat_history"
        db.execute_query(delete_query)
        # 2、删除token_history数据库中的短期数据
        delete_query = "DELETE FROM token_history"
        db.execute_query(delete_query)
        #3、清空网页的短期记忆
        st.session_state['short_history']=[]
        
    if st.session_state['tokens_compute']:
        st.sidebar.header(f"""Chat History tokens:{st.session_state['tokens_compute']}""")
    # if st.session_state['short_history']:
    show_STM()
       
    if user_input:
        # 用户输入
        st.session_state['user_input'] = user_input
        #向量数据获取
        # 创建AI_Response_API的实例
        aires = AI_Response_API()
        path1 = "/home/ubuntu/WeWork-OpenAI-Node/AI-npc-demo/Streamlis_Demos/victor_Demo/pages/test/dialog"
        info=aires.vector_file(input=st.session_state['user_input'],path =path1 )
        
        path2 = "/home/ubuntu/WeWork-OpenAI-Node/AI-npc-demo/Streamlis_Demos/victor_Demo/pages/test/src"
        info2=aires.vector_file(input=st.session_state['user_input'],path =path2 )
        
        # content = chat_completion.choices[0].message.content
        st.session_state['LTM_Vector_get']=info
        st.session_state['LTM_Vector_get_all'] = info
        #总prompt 
        st.session_state['total_prompt'] = f"""
            下面是对话的历史记录
            {st.session_state['short_history']}
            
            下面是与用户输入相关的额外提示
            {st.session_state['LTM_Vector_get']}
            下面是额外资料
            {info2}
            你需要根据上面我给出的提示和用户对话，尽可能回答用户问题,
            务必遵循以下几个规则：
            1、当对话的历史记录与额外提示发生冲突时,以对话的历史记录的信息为准
        """
        # 获取并流式显示AI响应
        ai_response = ai_res.stream_get_response(
            systemset=st.session_state['total_prompt'], 
            prompt=user_input
            )
        # 处理用户输入和AI响应
        handle_chat(user_input,ai_response)
        # 保存聊天记录到数据库
        save_chat_to_db(user_input, ai_response)
        # 保存聊天记录所消耗的tokens到数据库
        # 用户输入token
        input_tokens = token_compute(st.session_state['user_input'])
        # 总prompt tokens
        prompt_tokens = token_compute(st.session_state['total_prompt'])
        # aires_tokens tokens
        aires_tokens = token_compute(ai_response)
        #短期记忆 tokens
        STM_tokens = token_compute(st.session_state['short_history'])
        #向量记忆 tokens
        vector_tokens = token_compute(st.session_state['LTM_Vector_get'])
        #总token开销
        total_tokens = prompt_tokens+input_tokens+aires_tokens
        
        save_tokens_to_db(input_tokens,prompt_tokens,aires_tokens,STM_tokens,vector_tokens,total_tokens)
        st.session_state['token_history'] = get_token_data()
        
    
if __name__ == "__main__":
    
    
    main()
