import streamlit as st
from utils import *
from pathlib import Path
import os
import shutil
st.title("pdf文件替换以及测试")
st.write("仅支持PDF或Doc")

# 创建AI_Response_API的实例
aires = AI_Response_API()

# 文件上传器，允许用户上传文件
uploaded_file = st.file_uploader("Choose a file")

# 指定目标文件夹的路径
target_folder_path = "/home/ubuntu/WeWork-OpenAI-Node/AI-npc-demo/Streamlis_Demos/victor_Demo/pages/test/src"

# 定义标准文件名，用于在服务器上保存文件
standard_file_name = "standard_document.pdf"
# 指定要删除的文件夹名称（位于目标文件夹路径下）
folder_to_delete = ".vectordb"
if st.button("删除本地向量文件"):
     # 删除目标文件夹路径下的特定文件夹
    folder_to_delete_path = os.path.join(target_folder_path, folder_to_delete)
    if os.path.isdir(folder_to_delete_path):
        shutil.rmtree(folder_to_delete_path)
        st.success(f"文件夹 '{folder_to_delete}' 已被删除。")
    else:
        st.warning(f"未找到文件夹 '{folder_to_delete}'。")
# 如果用户上传了文件，则处理文件
if uploaded_file:
    # 用户输入，用于检索
    input = st.text_input("输入内容")
    # 检索按钮
    if st.button("检索"):
        # 获取目标文件路径，使用标准文件名
        target_file_path = os.path.join(target_folder_path, standard_file_name)

        # 将上传的文件保存到目标文件路径，并覆盖现有文件
        with open(target_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 调用AI_Response_API的方法处理文件
        st.write(aires.vector_file(input=input,path =target_folder_path ))
   
else:
    st.warning("请上传文件。")
