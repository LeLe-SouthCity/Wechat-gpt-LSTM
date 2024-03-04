import streamlit as st
from utils import *
from pathlib import Path

st.title("pdf文件替换以及测试")
st.write("仅支持PDF或Doc")

# 创建AI_Response_API的实例
aires = AI_Response_API()

# 文件上传器，允许用户上传文件
uploaded_file = st.file_uploader("Choose a file")

# 指定你想要列出文件夹的路径
path = Path(ROOT_DIR) / "victor_Demo" / "pages" / "src" / "test" 
# 使用Path对象的iterdir()方法列出所有子目录
folders = [item.name for item in path.iterdir() if item.is_dir()]
# 在文件夹列表前面插入一个空选项或者描述性占位符
folders.insert(0, '')  # 或者使用空字符串 ''
# 使用Streamlit的selectbox让用户选择一个文件夹
selected_tag = st.sidebar.selectbox("选择已保存的文件",folders)

# 初始化文件路径
file_path = None

# 检查用户是否已经选择了一个文件夹
if selected_tag:
    st.info(f"""已选择文件{selected_tag}""")
    # 由于每个文件夹下只有一个文件，我们可以直接获取该文件
    folder_path = path / selected_tag
    file_path = next(folder_path.iterdir(), None)  # 获取第一个文件路径
    

# 如果用户上传了文件或选择了现有文件，则处理文件
if uploaded_file or file_path:
    # 用户输入，用于检索
    input = st.text_input("输入内容")
    
    # 检索按钮
    if st.button("检索"):
        # 如果用户上传了文件，使用上传的文件
        if uploaded_file:
            file_to_process = uploaded_file
            # 调用AI_Response_API的方法处理文件
            aires.savefile_A_getInfo( input=input,uploaded_file=file_to_process)
        # 否则，使用选择的文件路径
        else:
            aires.savefile_A_getInfo(input=input,file_name=selected_tag)
else:
    st.warning("请上传文件或从列表中选择一个文件。")
