import datetime
import json
import os
import sys
import streamlit as st
import matplotlib.pyplot as plt
from Vector_Utils.vector_api import *

from pathlib import Path

# 获取 utils.py 所在的文件夹路径
utils_path = os.path.abspath('/home/ubuntu/WeWork-OpenAI-Node/AI-npc-demo/Streamlis_Demos/Utils')

# 将 utils.py 所在的文件夹添加到 sys.path
if utils_path not in sys.path:
    sys.path.append(utils_path)
    
from utils import *

st.set_page_config(
    page_title="历史记录查看&&向量数据检索",
    page_icon="👋",
)

json_file_path = Path(ROOT_DIR) / "victor_Demo" / "chat_history.json" 
word_file_path = Path(ROOT_DIR) / "victor_Demo" / "pages" / "test" /"output_file.docx"
st.sidebar.write("短期记忆")
st.sidebar.write(st.session_state['short_history'])
def calculate_average(df, column_name):
    if len(df) > 10:
        sample_df = df.sample(n=10)
        average = sample_df[column_name].mean()
    else:
        average = df[column_name].mean()
    return average
#数据获取
# 检查是否有数据
if st.session_state.get('token_history'):
    with st.container():
        # 将token_history转换为DataFrame并指定列名
        df_tokens = pd.DataFrame(st.session_state['token_history'], columns=[
            'Input Tokens', 'Prompt Tokens', 'Aires Tokens', 
            'STM Tokens', 'Vector Tokens', 'Total Tokens'
        ])
        
        
        # 计算平均值
        input_tokens_avg = calculate_average(df_tokens, 'Input Tokens')
        prompt_tokens_avg = calculate_average(df_tokens, 'Prompt Tokens')
        aires_tokens_avg = calculate_average(df_tokens, 'Aires Tokens')
        STM_tokens_avg = calculate_average(df_tokens, 'STM Tokens')
        vector_tokens_avg = calculate_average(df_tokens, 'Vector Tokens')
        other_prompt_tokens_avg = prompt_tokens_avg - STM_tokens_avg - vector_tokens_avg
        # 准备饼状图数据
        outer_sizes_avg = [input_tokens_avg, prompt_tokens_avg, aires_tokens_avg]  # 外环平均数据
        inner_sizes_avg = [STM_tokens_avg, vector_tokens_avg, other_prompt_tokens_avg]  # 内环平均数据
        
        # token的标签和颜色
        outer_labels = ['Input Tokens', 'Prompt Tokens', 'airesponse Tokens']
        outer_colors = ['#73e5ed', '#f0593e', '#e0e77a']
        
        # 总prompt标签和颜色
        inner_labels = ['STM Tokens', 'Vector Tokens', 'Other Prompt Tokens']
        inner_colors = ['lightcoral', 'gold', 'lightblue']
    
else:
    st.write("No token data available to display.")

tab1, tab2,tab3,tab4,tab5= st.tabs(["长期记忆和检索的向量记忆", "向量记忆检索","总Prompt显示","短期记忆tokens开销表","tokens可视化饼状图"])
with tab1:
    
    col1,col2 = st.columns(2)
    with col1:
        with open("chat_history.json", 'rb') as file:
            st.download_button(
                label="Download JSON",
                data=file,
                file_name="file.json",
                mime="application/json"
            )
        st.title("json长期记忆")
        try:
            # 打开 JSON 文件并读取其内容
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
            
            # 使用 Streamlit 显示 JSON 数据
            # 这里我们假设 JSON 数据是一个字典或列表
            st.json(data)
        except Exception as e:
            st.error(f"An error occurred while reading the JSON file: {e}")
    with col2:  
        st.title("向量记忆显示")
        if st.session_state['LTM_Vector_get']:
            st.write(st.session_state['LTM_Vector_get'])
with tab2:
    
    st.title("向量记忆检索")
    
    # 将json转为word
    convert_json_to_word(json_file_path, word_file_path)

    # 创建AI_Response_API的实例
    aires = AI_Response_API()

    # 用户输入，用于检索
    input = st.text_input("输入内容")
        
    # 检索按钮
    if st.button("检索"):
        path = Path(ROOT_DIR) / "victor_Demo" / "pages" / "test" 
        info=aires.vector_file(input=input,path =path )
        # content = chat_completion.choices[0].message.content
        cola,colb =  st.columns(2)
        with cola:
            st.success("检索内容")
            st.write(info)
        # with colb:
            # st.success("总结内容")
            # st.write(content)

with tab3:
    st.title("总Prompt显示")
    if st.session_state['total_prompt']:
        st.write(st.session_state['total_prompt'])

with tab4:
    # 使用 Streamlit 展示表格，现在它有了列名
    try:
        st.table(df_tokens)
    except Exception as e:
        st.error("暂时未开启新的对话")
    
        
with tab5:
    try:
        col3, col4 = st.columns(2)
        # 绘制总token的平均饼状图
        with col3:
            st.write("总token的平均饼状图")
            fig1, ax1 = plt.subplots(figsize=(8, 6))
            ax1.pie(outer_sizes_avg, labels=outer_labels, radius=1.0, colors=outer_colors,
                autopct='%1.1f%%', pctdistance=0.85, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            # 使用 Streamlit 展示外环饼状图
            st.pyplot(fig1)

        # 绘制总prompt的平均饼状图
        with col4:
            st.write("总prompt的平均饼状图")
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            ax2.pie(inner_sizes_avg, labels=inner_labels, radius=1.0, colors=inner_colors,
                autopct='%1.1f%%', pctdistance=0.85, startangle=90)
            ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            # 使用 Streamlit 展示内环饼状图
            st.pyplot(fig2)
    except Exception as e:
        st.error("暂时未开启新的对话")
                
                