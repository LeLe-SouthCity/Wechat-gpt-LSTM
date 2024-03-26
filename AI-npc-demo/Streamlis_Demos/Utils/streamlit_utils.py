import streamlit as st
import os


def select_file_from_folder(
    folder_path:str, 
    file_types:list=None
    ):
    """
    在 Streamlit 应用中创建一个选择框，允许用户从指定文件夹中选择特定类型的文件。
    
    参数:
    - folder_path(str): 文件夹的路径
    - file_types(str): 可接受的文件类型集合，例如 {'.mp3', '.wav'}
    
    返回:
    - selected_file_path: 选中文件的完整路径，如果没有文件被选中则为 None
    # 使用示例
    # 假设我们想要让用户从 'testaudios' 文件夹中选择 '.mp3' 或 '.wav' 文件
    folder_path = 'testaudios'
    file_types = {'.mp3', '.wav'}
    selected_file_path = select_file_from_folder(folder_path, file_types)
    """
    # 检查文件类型是否被指定，如果没有，则接受所有类型的文件
    if file_types is None:
        # 获取文件夹中所有文件
        audio_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    else:
        # 确保 file_types 是集合类型
        file_types_set = set(file_types)
        # 获取文件夹中所有符合类型的文件
        audio_files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1] in file_types_set]
    
    # 如果文件夹中有文件，则显示一个选择框供用户选择
    if audio_files:
        selected_file = st.selectbox('Select a file:', audio_files)
        
        # 获取选中文件的完整路径
        selected_file_path = os.path.join(folder_path, selected_file)
        return selected_file_path
    else:
        st.write("No files found with the given types in the folder.")
        return None
    