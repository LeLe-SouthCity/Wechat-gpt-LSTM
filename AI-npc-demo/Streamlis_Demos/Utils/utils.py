from openai import OpenAI
import requests
import json
import streamlit as st
import io
import base64
import datetime
import re
from Script_Set import *
import asyncio
from docx import Document
from PIL import Image, ImageDraw
import numpy as np
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from app_config import *
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import dotenv
dotenv.load_dotenv()
import base64
from io import BytesIO,StringIO
from docx import Document
from streamlit_image_select import image_select
import pandas as pd
import fitz  # PyMuPDF
import time

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','Code')))
from langchain_api import *
os.environ["OPENAI_API_KEY"] = OpenAI_Key
#-----------------一些常用办法----------------------------
# 将url格式转为 base64 编码的字符串
def url_to_base64(
    image_url:str
    ):
    """
    将url格式转为 base64 编码的字符串
    image_url(str):图像资源的 URL的字符串类型
    """
    # 发送 GET 请求下载图像
    response = requests.get(image_url)
    
    # 确保请求成功
    if response.status_code == 200:
        # 获取图像的字节内容
        image_bytes = response.content
        
        # 使用 base64 编码图像字节内容
        b64_encoded = base64.b64encode(image_bytes)
        
        # 将 base64 编码转换为 UTF-8 格式的字符串
        b64_string = b64_encoded.decode('utf-8')
        
        # 返回 base64 编码的字符串
        return b64_string
    else:
        raise Exception(f"Failed to download image. Status code: {response.status_code}")

# 根据选定的标签获取声音数据
def get_data_by_tag_audio(selected_tag, filename="Audio.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            # 确保数据是列表格式
            if not isinstance(data, list):
                data = [data]
    except FileNotFoundError:
        data = []
    # 查找匹配的标签并返回对应的数据
    for item in data:
        if item.get('tag') == selected_tag:
            return item
    return None

#侧边栏显示已选择的图片
def Avatar_sidebar_Display():
    """
    侧边栏显示用户显示的头像
    """
    # 假设这是用户选择的头像的base64字符串
    selected_avatar_base64 = st.session_state.get('selected_avatar')
    # 如果用户已经选择了头像，则在边栏中显示
    if selected_avatar_base64:
        st.sidebar.header("已选择的头像")
        # 将base64字符串转换为PIL图像
        image_data = base64.b64decode(selected_avatar_base64)
        image = Image.open(io.BytesIO(image_data))
        # 在边栏中显示图像
        st.sidebar.image(image, width=100)  # 控制图片的显示大小
    else:
        st.sidebar.header("头像未选择")

#通过prompt获取SD 的图片                  
async def get_images_SD(image_prompt: str, num_images: int):
    """
    获取多个图片的b64格式列表
    image_prompt: 图片的prompt设置
    num_images: 要生成的图片数量
    """
    # 获取API
    stability_api = client.StabilityInference(
        key=stability_api_key,  # 替换为你的API Key
        engine=Engine,  # 设置使用的生成引擎
    )
    
    # 根据输出创建图片提示
    api_res = stability_api.generate(
        prompt=image_prompt,
        steps=30,
        width=512,
        height=512,
        samples=num_images,  # 设置要生成的图片数量
    )
    
    # 从Stability AI响应中提取所有图片的base64编码
    b64str_list = []
    for resp in api_res:
        for artifact in resp.artifacts:
            if artifact.type == generation.ARTIFACT_IMAGE:
                b64str = base64.b64encode(artifact.binary).decode("utf-8")
                b64str_list.append(b64str)
                if len(b64str_list) == num_images:
                    return b64str_list
    
    # 检查是否生成了所需数量的图片
    if len(b64str_list) == num_images:
        return b64str_list
    else:
        st.error("图片生成错误或生成的图片数量不足")
        return False
   
#用于使用opeai获取Sd的prompt
def generate_image_prompt_SD(description):
    """
    获取SD生成图片的前置prompt
    description(str):为人物的设定集
    """
    prompt = f"""
    Based on the provided description "{description}",
    The Stable Diffusion prompt you output begins with "Prompt:".
    The prompt content includes the main body of the picture, material, additional details, image quality, artistic style, color tone, lighting, etc., but the prompt you output cannot be segmented. For example, segmented descriptions like "medium:" are not needed, nor Cannot contain ":" and ".".
    Main body of the picture: A non-brief English description of the main body of the picture, such as A girl in a garden, a summary of the subject details (the subject can be a person, thing, object, or scene) and the core content of the picture. This part is generated based on the theme I give you each time. You can add more details that are relevant and relevant to the topic.
    For character themes, you must describe the character’s eyes, nose, and lips, such as ‘beautiful detailed eyes, beautiful detailed lips, extremely detailed eyes and face, longeyelashes’ to avoid Stable Diffusion from randomly generating deformed facial features, which is very important. You can also describe the character's appearance, mood, clothes, posture, perspective, actions, background, etc. In the character attributes, 1girl represents one girl, and 2girls represents two girls.
    Material: The material used to make the artwork. For example: illustration, painting, 3D rendering and photography.
    Additional details: scene details, or character details, describe the details of the picture and make the image look more substantial and reasonable. This part is optional. Pay attention to the overall harmony of the picture and not conflict with the theme.
    Image quality: Always add "(best quality, 4k, 8k, highres, masterpiece: 1.2), ultra-detailed, (realistic, photorealistic, photo-realistic: 1.37)" at the beginning of this part of the content. This is a sign of high quality. . You can add according to the needs of the theme: HDR, UHD, studio lighting, ultra-fine painting, sharp focus, physically-based rendering, extreme detail description, professional, vivid colors, bokeh.
    Art Style: This section describes the style of the image. Adding the appropriate artistic style can enhance the resulting image. Commonly used art styles include: portraits, landscape, horror, anime, sci-fi, photography, concept artists, etc.
    Color Tone: Color, control the overall color of the picture by adding color.
    Lighting: The lighting effect of the overall picture.
    """
    # gpt_prompt_text = st.text_area('图片prompt设置', value=prompt)
    optimized_chunk = OpenAI(temperature=1.0)(prompt)
    return optimized_chunk


#AI回复类

#AI回复类
class AI_Response_API():
    """
    提供了一个流式显示ai回复的办法
    """
    def __get_stream_response(
        self,
        systemset:str,
        prompt:str,
        stream=True
    ):
        """
        使用__进行私有化 --- 不要调用
        异步函数获取回复的方法，无法直接运行，需要通过sync_get_images方法运行

        Args:
            systemset (str): AI扮演角色的prompt
            prompt (str): Ai与用户的对话历史记录

        Returns:
            (str): 返回一个str类型的字符串
        """
        response = OPenaiClient.chat.completions.create(
                        # model="gpt-3.5-turbo-16k",
                        model="gpt-4-1106-preview",
                        messages=[
                            {"role": "system", "content":systemset },
                            {"role": "user", "content": prompt}
                        ],
                        stream=stream
                    )
        
        return response 


    def stream_get_response(
        self,
        systemset:str,
        prompt:str
    ):
        """
        逐字显示
        流式显示回复

        Args:
            systemset (str): AI扮演角色的prompt
            prompt (str): Ai与用户的对话历史记录
            
        Returns:
            (str): 返回一个str类型的字符串
        """
        # 获取 GPT 的流式回复
        message_placeholder = st.empty()
        full_response = ""
        for response in self.__get_stream_response(systemset=systemset,prompt=prompt):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        #传送给openai后清空
        message_placeholder.markdown(full_response)
        return full_response
    
    def __get_sum_info(
        self,
        info:str,
        stream=True
    ):
        """
        获取与用户输入相关的内容并进行总结

        Args:
            info (str): 相关的内容
            inuput (str): 用户的输入内容

        Returns:
            str: 返回一个总结的内容
        """
        
        if stream:
            prompt = f"""
            请根下面的向量数据库检索结果进行分析，并提炼出关键信息。
            "{info}"
            """
            return self.stream_get_response(systemset=prompt,prompt=prompt)
        else:
            prompt = f"""
            请根下面的向量数据库检索结果进行分析，并提炼出关键信息。
            "{info}"
            """
            return self.__get_stream_response(systemset=prompt,prompt=prompt,stream=stream)
     
    def vector_file(self,input,path):
        vectors=KnownLedge2Vector(
                                dbpath=path,
                                datasetdir=path,
                                model_name=1,
                                chunk_size=500,
                                chunk_overlap=0
                                ).init_vector_store()
        task = MyTask(
            # "gpt-3.5-turbo-1106"
                    llm=LLM_Model(llm_model_type=1,temperature = 0.7).get_model(modelname="gpt-3.5-turbo-1106"),
                    # retriever=vectors.as_retriever(
                    #     search_type="mmr",
                    #     search_kwargs={'k': 3, 'fetch_k': 50, 'lambda_mult': 0.25}
                    # )
                    retriever=vectors.as_retriever(
                        search_type="mmr",
                        search_kwargs={'k': 6, 'lambda_mult': 0.5}
                    )
                )
        info = task.query(question=input)
        # self.__get_sum_info(info=info,inuput=input,stream=False)
        return info
           
    def savefile_A_getInfo(
        self,
        uploaded_file:str =None,
        input:str = None,
        file_name :str = None,
    ):
        """
        逐字输出总结后的与输入相关的文档内容

        Args:
            uploaded_file (_type_): streamlit上传的文件
            input (str): 输入的内容

        Returns:
            (str): 返回总结后的信息
        """
        functions = Streamlist_Functions()
        vectors = None  # 初始化vectors变量
        task = None 
        
        if uploaded_file is not None or file_name is not None:
            if file_name :
                path = os.path.join(ROOT_DIR,"victor_Demo", "pages", "src","files",file_name)
            if uploaded_file:
                path = os.path.join(ROOT_DIR,"victor_Demo", "pages", "src","files",uploaded_file.name)
                
            try:
                functions.save_file(path=path,uploaded_file=uploaded_file)
                st.success("文件保存成功")
            except:
                st.error("文件保存成功")
                
            vectors=KnownLedge2Vector(
                                dbpath=path,
                                datasetdir=path,
                                model_name=1,
                                chunk_size=500,
                                chunk_overlap=0
                                ).init_vector_store()
                
            task = MyTask(
            # "gpt-3.5-turbo-1106"
                    llm=LLM_Model(llm_model_type=1,temperature = 0.7).get_model(modelname="gpt-3.5-turbo-1106"),
                    # retriever=vectors.as_retriever(
                    #     search_type="mmr",
                    #     search_kwargs={'k': 3, 'fetch_k': 50, 'lambda_mult': 0.25}
                    # )
                    retriever=vectors.as_retriever(
                        search_type="mmr",
                        search_kwargs={'k': 6, 'lambda_mult': 0.5}
                    )
                )
            
            return self.__get_sum_info(info=task.query(question=input))
               
              
# 自定义streamlit办法
class Streamlist_Functions():
    # 定义一个函数,自动识别并生成选项radio
    def str_to_radio(
        self,
        radio_title:str,
        text:str
        ):
        """
        output选项 St.radio
        str转radio

        Args:
            radio_title (str): radio标题
            text (str): 需要转换tadio的正文

        Returns:
            choice_index(int): 返回选择是第几个选项
            choice(str):返回选择的内容
        """
        if text is None:
            st.error("字符串为空")
        # 使用正则表达式匹配可能的选项
        # 匹配以大写字母或数字开头，后面接一个点和空格，然后是任意字符的模式
        options = re.findall(r'^[A-Z0-9]\.\s*(.+)$', text, re.MULTILINE)
        
        if len(options) == 0:
            return None,None
        
        # 显示radio
        choice = st.radio(radio_title, options)
        # 找出用户选择的选项的索引
        choice_index = options.index(choice) + 1  # 加 1 是因为列表索引从 0 开始，但选项通常从 1 开始编号
        return choice_index,choice
    
    #进度条显示
    def time_to_progress(
        self,
        time_sleep:int
    ):
        """
        长Prompt 加载output进度条显示

        Args:
            time_sleep (float): 进度条时间设置
        """
        total_duration = time_sleep*10  # 总持续时间（秒）
        update_interval = 0.1  # 更新间隔（秒）
        progress_bar = st.progress(0)

        for i in range(total_duration):
            # 计算进度百分比
            percent_complete = int(((i + 1) / total_duration) * 100)
            # 更新进度条
            progress_bar.progress(percent_complete)
            # 模拟长时间运行的任务
            time.sleep(update_interval)

    #文件上传
    def file_uploader(
        self,
        st_container,
        key:str,
        uploader_title:str = "上传文件")->str:
        """
        PDF、doc 文件上传方法`
        
        Args:
            st_container: Streamlit 容器，可以是 st 或 st.sidebar
            key(str): 用于确保每个文件上传器的唯一性的键
            uploader_title(str):问价上传按钮的标题
        Returns:
            (str|None): 文件不为空则返回一个str类型的，否则返回None
        """
        uploaded_file = st_container.file_uploader(uploader_title,key=key)
        if uploaded_file is not None:
            # 检查上传的文件是否是 PDF 文档
            if uploaded_file.type == "application/pdf":
                # 将上传的文件转换为字节流
                bytes_data = BytesIO(uploaded_file.read())
                # 读取 PDF 文件内容
                with fitz.open(stream=bytes_data, filetype="pdf") as doc:
                    text = ""
                    # 遍历每一页
                    for page in doc:
                        # 提取页面的文本
                        text += page.get_text()
                    # 检查提取的文本是否为空
                    if text.strip():  # 使用 strip() 来移除可能的空白字符
                        # 显示 Word 文件的文本内容
                        # st_container.text_area(label = uploader_title,value = text,height=100)
                        return text
                    else:
                        # 如果文本为空，显示错误消息
                        st_container.info("文件为空")
                    # return text
            # 检查上传的文件是否是 Word 文档
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                # 将上传的文件转换为字节流
                bytes_data = BytesIO(uploaded_file.read())
                # 读取 Word 文档内容
                doc = Document(bytes_data)
                text = ""
                for para in doc.paragraphs:
                    text += para.text + '\n'
                # 检查提取的文本是否为空
                if text.strip():  # 使用 strip() 来移除可能的空白字符
                    # 显示 Word 文件的文本内容
                    # st_container.text_area(label = uploader_title,value = text,height=100)
                    return text
                else:
                    # 如果文本为空，显示错误消息
                    st_container.error("文件为空")
        else:
            st_container.info('☝️ Upload a pdf/docs file')
        return None

    # 用于上传文件并保存在本地文件夹（文字命名的）
    def save_file(self,path,uploaded_file):
        """_summary_

        Args:
            path (_type_): 文件的保存路径
            uploaded_file (_type_): 文件名称

        Returns:
            _type_: 保存成功与否
        """
        if not os.path.exists(path):  # Create the path if it doesn't exist
            os.makedirs(path)
        if uploaded_file is not None:
            # Define the local filename where to save the file
            local_filename = os.path.join(path, uploaded_file.name)
            
            # Save the uploaded file to the local filesystem
            with open(local_filename, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            st.success('File saved locally as {}'.format(local_filename))
            return True
        return False


# Demo 类------------------------------------------------
class Dialog_Demo():
    def get_base64_encoded_audio(self,audio_path):
        """
        读取MP3文件并转换为base64编码：
        """
        with open(audio_path, "rb") as audio_file:
            return base64.b64encode(audio_file.read()).decode('utf-8')

    # 定义一个函数来根据tag获取数据
    def get_data_by_tag(self,tag):
        # 假设json_file_path是你的JSON文件的路径
        json_file_path = 'Audio.json'

        # 读取JSON文件
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)

        for entry in json_data:
            if entry.get('tag') == tag:
                if 'male' in entry:
                    return 'male', entry['male']
                elif 'female' in entry:
                    return 'female', entry['female']
        return None, None        
 
    async def set_audio(
        self,
        text:str,
        gender:str,
        audiopath:str,
        male_qn_qingse=1 ,
        male_qn_jingying=1,
        male_qn_badao=1,
        male_qn_daxuesheng=1 ,
        female_shaonv=1,
        female_yujie=1,
        female_chengshu=1,
        female_tianmei=1,
    ):
        """
        获取声音的b64格式
        text(str):转换的文本
        gender(str):角色性别
        audiopath(str):保存声音的路径
        """
        if gender=="male":
            # 这两个下一步再改,默认的问题也不大
            speed = 1.0
            vol = 1.0
            group_id = "1689852985712348"
            api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJOYW1lIjoidGVzdCIsIlN1YmplY3RJRCI6IjE2ODk4NTI5ODU1OTczOTIiLCJQaG9uZSI6Ik1UVTRNVFU0TURJNU1qUT0iLCJHcm91cElEIjoiMTY4OTg1Mjk4NTcxMjM0OCIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6InpseWdpbGlhbmFAc2luYS5jb20iLCJDcmVhdGVUaW1lIjoiMjAyMy0wOS0wNSAwMDoyNjo1NSIsImlzcyI6Im1pbmltYXgifQ.gdr3NXX8bAKN9E0bzuVsX5HhGXfHnZRY7YEjzo36_CYXUSDDZ4ZZTTopRJ1SLo9O_bOXJ0pnw2FJHz4kVvOedHbrBXbXHAFwyjWZfZ1kP0iE_n11EEClyIXizUvrh35m1DjPhMiPMYXJpVWy5dIkcD7UHBpZCw3DRk68I8XxdkFkZ3LHmBNqvbH9isTRiCzXUprnk2FwfrU8y38-K-H0mzhzJwxNYCO7SuOr26ZBJGDfPGS8K-X2WCJSYUH6pWwocGBrT10Du4A5qH03Eri0xQ4zs1O08G8tYkp4vWhdcNo7iXMDwGeV-BT5yFup6toAFu7CoU-ge30szOv-6AMsSw"

            url = f"https://api.minimax.chat/v1/text_to_speech?GroupId={group_id}"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "text": text,
                "model": "speech-02",
                "speed": speed,
                "vol": vol,
                "pitch": 0,
                "timber_weights": [
                    {
                        "voice_id": "male-qn-qingse",
                        "weight": male_qn_qingse
                    },
                    {
                        "voice_id": "male-qn-jingying",
                        "weight": male_qn_jingying
                    },
                    {
                        "voice_id": "male-qn-badao",
                        "weight": male_qn_badao
                    },
                    {
                        "voice_id": "male-qn-daxuesheng",
                        "weight": male_qn_daxuesheng
                    },
                ]
            }

            response = requests.post(url, headers=headers, json=data)
            print("trace_id", response.headers.get("Trace-Id"))
            if response.status_code == 200:
                with open(audiopath, "wb") as f:
                    f.write(response.content)
                # st.success('Conversion successful!')
                st.balloons()

            else:
                st.error('Failed to convert text to speech.')

        elif gender=="female":
            group_id = "1689852985712348"
            api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJOYW1lIjoidGVzdCIsIlN1YmplY3RJRCI6IjE2ODk4NTI5ODU1OTczOTIiLCJQaG9uZSI6Ik1UVTRNVFU0TURJNU1qUT0iLCJHcm91cElEIjoiMTY4OTg1Mjk4NTcxMjM0OCIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6InpseWdpbGlhbmFAc2luYS5jb20iLCJDcmVhdGVUaW1lIjoiMjAyMy0wOS0wNSAwMDoyNjo1NSIsImlzcyI6Im1pbmltYXgifQ.gdr3NXX8bAKN9E0bzuVsX5HhGXfHnZRY7YEjzo36_CYXUSDDZ4ZZTTopRJ1SLo9O_bOXJ0pnw2FJHz4kVvOedHbrBXbXHAFwyjWZfZ1kP0iE_n11EEClyIXizUvrh35m1DjPhMiPMYXJpVWy5dIkcD7UHBpZCw3DRk68I8XxdkFkZ3LHmBNqvbH9isTRiCzXUprnk2FwfrU8y38-K-H0mzhzJwxNYCO7SuOr26ZBJGDfPGS8K-X2WCJSYUH6pWwocGBrT10Du4A5qH03Eri0xQ4zs1O08G8tYkp4vWhdcNo7iXMDwGeV-BT5yFup6toAFu7CoU-ge30szOv-6AMsSw"
            speed = 1.0
            vol = 1.0
                
            url = f"https://api.minimax.chat/v1/text_to_speech?GroupId={group_id}"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            data = {
                # "voice_id": "female-yujie-jingpin",
                # 如同时传入voice_id和timber_weights时，则会自动忽略voice_id，以timber_weights传递的参数为准
                "text": text,
                "model": "speech-02",
                "speed": speed,
                "vol": vol,
                "pitch": 0,
                "timber_weights": [

                    {
                        "voice_id": "female-shaonv",
                        "weight": female_shaonv
                    },
                    {
                        "voice_id": "female-yujie",
                        "weight": female_yujie
                    },
                    {
                        "voice_id": "female-chengshu",
                        "weight": female_chengshu
                    },
                    {
                        "voice_id": "female-tianmei",
                        "weight": female_tianmei
                    },

                ]
            }
            response = requests.post(url, headers=headers, json=data)
            print("trace_id", response.headers.get("Trace-Id"))
            if response.status_code == 200:
                with open(audiopath, "wb") as f:
                    f.write(response.content)
                # st.success("转换成功!")
                st.balloons()
            else:
                st.error("出错了,请查看报错信息!")
            
#角色创建的Demo
class Role_Infoset(
    
):
    """
    角色信息获取
    """
    
    def get_role_image(
        self,
        image_path:str
    ):
        # 加载图像
        image = Image.open(image_path)
        # 创建和图像同样大小的遮罩
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + image.size, fill=255)

        # 应用遮罩到图像
        result = Image.new('RGBA', image.size)
        # result.paste(image, (0, 0), mask)
        res = result.paste(image, (0, 0), mask)
        return res

#混音页面设置
class Audio_display():
    
    def __init__(self):
        # 定义可选的音色参数及其描述
        self.voice_options = {
            "空": None,
            "青涩青年音色": "male-qn-qingse",
            "精英青年音色": "male-qn-jingying",
            "霸道青年音色": "male-qn-badao",
            "青年大学生音色": "male-qn-daxuesheng",
            "少女音色": "female-shaonv",
            "御姐音色": "female-yujie",
            "成熟女性音色": "female-chengshu",
            "甜美女性音色": "female-tianmei",
            "男性主持人": "presenter_male",
            "女性主持人": "presenter_female",
            "男性有声书1": "audiobook_male_1",
            "男性有声书2": "audiobook_male_2",
            "女性有声书1": "audiobook_female_1",
            "女性有声书2": "audiobook_female_2",
            "青涩青年音色-beta": "male-qn-qingse-jingpin",
            "精英青年音色-beta": "male-qn-jingying-jingpin",
            "霸道青年音色-beta": "male-qn-badao-jingpin",
            "青年大学生音色-beta": "male-qn-daxuesheng-jingpin",
            "少女音色-beta": "female-shaonv-jingpin",
            "御姐音色-beta": "female-yujie-jingpin",
            "成熟女性音色-beta": "female-chengshu-jingpin",
            "甜美女性音色-beta": "female-tianmei-jingpin",
            "超级色色":"wuzhao_test_2",
        }
    
    def save_to_json(
        self,
        new_data,
        tag,
        filename="Audio.json"
        ):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []

        # 检查data是否为列表，如果不是，则将其转换为列表
        if not isinstance(data, list):
            data = [data]

        # 检查标签是否已存在
        for entry in data:
            if entry.get("tag") == tag:
                return False  # 返回False表示标签已存在

        # 添加新数据到列表中
        data.append(new_data)

        with open(filename, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return True  # 返回True表示保存成功

    def get_mp3(
        self,
        gender:str="男",
        outputmp3:str="output.mp3",
        ):

        
        # 创建一个下拉菜单，让用户选择一个音色
        voice_id_set = self.voice_options[st.selectbox("请选择一个音色:", list(self.voice_options.keys()))]
        # st.info(voice_id_set)
        """
        gender(str):性别设置
        outputmp3(str):输出的语音文件
        """
        if gender=="男":
            st.info("自由拖动滑杆,创造你的专属男角色音线")
            if voice_id_set == None:
                male_qn_qingse = st.slider("正太", 1, 100, 1)
                male_qn_jingying = st.slider("成熟", 1, 100, 100)
                male_qn_badao = st.slider("霸道", 1, 100, 1)
                male_qn_daxuesheng = st.slider("阳光", 1, 100, 1)
            speed = st.slider("语速", 0.5, 2.0, 1.0)
            pitch = st.slider("生成声音的语调", -12, 12, 0)

            # 这两个下一步再改,默认的问题也不大
            vol = 1.0
            group_id = "1689852985712348"
            api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJOYW1lIjoidGVzdCIsIlN1YmplY3RJRCI6IjE2ODk4NTI5ODU1OTczOTIiLCJQaG9uZSI6Ik1UVTRNVFU0TURJNU1qUT0iLCJHcm91cElEIjoiMTY4OTg1Mjk4NTcxMjM0OCIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6InpseWdpbGlhbmFAc2luYS5jb20iLCJDcmVhdGVUaW1lIjoiMjAyMy0wOS0wNSAwMDoyNjo1NSIsImlzcyI6Im1pbmltYXgifQ.gdr3NXX8bAKN9E0bzuVsX5HhGXfHnZRY7YEjzo36_CYXUSDDZ4ZZTTopRJ1SLo9O_bOXJ0pnw2FJHz4kVvOedHbrBXbXHAFwyjWZfZ1kP0iE_n11EEClyIXizUvrh35m1DjPhMiPMYXJpVWy5dIkcD7UHBpZCw3DRk68I8XxdkFkZ3LHmBNqvbH9isTRiCzXUprnk2FwfrU8y38-K-H0mzhzJwxNYCO7SuOr26ZBJGDfPGS8K-X2WCJSYUH6pWwocGBrT10Du4A5qH03Eri0xQ4zs1O08G8tYkp4vWhdcNo7iXMDwGeV-BT5yFup6toAFu7CoU-ge30szOv-6AMsSw"

            text = st.text_area('输入文本 在字间增加<#x#>,x单位为秒，支持0.01-99.99s，最多两位小数）',  "爱像一阵风,吹完它就走,这样的节奏,谁都无可奈何,没有妳以后,我灵魂失控,黑云在降落,我被它拖着走,静静,悄悄,默默,离开,陷入了危险边缘")
            col1, col2 = st.columns(2)
            with col1:
                if st.button('文本转语音'):
                    url = f"https://api.minimax.chat/v1/text_to_speech?GroupId={group_id}"
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }
                    if voice_id_set:
                        data = {
                            "voice_id":voice_id_set,
                            "text": text,
                            "model": "speech-02",
                            "speed": speed,
                            "vol": vol,
                            "pitch": pitch
                        }
                    else:
                        data = {
                            "text": text,
                            "model": "speech-02",
                            "speed": speed,
                            "vol": vol,
                            "pitch": pitch,
                            "timber_weights": [
                                {
                                    "voice_id": "male-qn-qingse",
                                    "weight": male_qn_qingse
                                },
                                {
                                    "voice_id": "male-qn-jingying",
                                    "weight": male_qn_jingying
                                },
                                {
                                    "voice_id": "male-qn-badao",
                                    "weight": male_qn_badao
                                },
                                {
                                    "voice_id": "male-qn-daxuesheng",
                                    "weight": male_qn_daxuesheng
                                },
                            ]
                        }

                    response = requests.post(url, headers=headers, json=data)
                    print("trace_id", response.headers.get("Trace-Id"))
                    if response.status_code == 200:
                        with open("output.mp3", "wb") as f:
                            f.write(response.content)
                        st.success('Conversion successful!')
                        st.balloons()
                        # st.audio("output.mp3", format='audio/mp3')
                        with open("output.mp3", "rb") as f:
                            audio_bytes = f.read()

                        st.audio(audio_bytes, format="audio/mp3")

                    else:
                        st.error('Failed to convert text to speech.')
            with col2:     
                    # 添加保存权重的按钮（男性部分）
                    if st.button('保存男性角色权重'):
                        # 在保存之前添加标签输入框
                        voice_tag = st.text_input('输入这个声音的标签（例如：温柔、阳光等）', '')
                        if voice_tag:  # 确保用户输入了标签
                            male_weights = {
                                "male-qn-qingse": male_qn_qingse,
                                "male-qn-jingying": male_qn_jingying,
                                "male-qn-badao": male_qn_badao,
                                "male-qn-daxuesheng": male_qn_daxuesheng
                            }
                            # 将标签和权重打包成新数据
                            new_data = {"male": male_weights, "tag": voice_tag}
                            # 调用save_to_json函数并检查返回值
                            if self.save_to_json(new_data, voice_tag):
                                st.success("男性角色权重和标签已保存到本地文件")
                            else:
                                st.error("该名称已存在，请使用其他标签。")
                        else:
                            st.error("请先输入声音标签再保存权重。")

        elif gender=="女":
            st.info("自由拖动滑杆,创造你的专属女角色音线")
            
            if voice_id_set == None:
                female_shaonv = st.slider("少女", 1, 100, 1)
                female_yujie = st.slider("御姐", 1, 100, 1)
                female_chengshu = st.slider("成熟", 1, 100, 100)
                female_tianmei = st.slider("甜美", 1, 100, 1)
            speed = st.slider("语速", 0.5, 2.0, 1.0)
            pitch = st.slider("生成声音的语调", -12, 12, 0)
            text = text = st.text_area('输入文本 在字间增加<#x#>,x单位为秒，支持0.01-99.99s，最多两位小数）', 
                                "爱像一阵风,吹完它就走,这样的节奏,谁都无可奈何,没有妳以后,我灵魂失控,黑云在降落,我被它拖着走,静静,悄悄,默默,离开,陷入了危险边缘")

            group_id = "1689852985712348"
            api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJOYW1lIjoidGVzdCIsIlN1YmplY3RJRCI6IjE2ODk4NTI5ODU1OTczOTIiLCJQaG9uZSI6Ik1UVTRNVFU0TURJNU1qUT0iLCJHcm91cElEIjoiMTY4OTg1Mjk4NTcxMjM0OCIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6InpseWdpbGlhbmFAc2luYS5jb20iLCJDcmVhdGVUaW1lIjoiMjAyMy0wOS0wNSAwMDoyNjo1NSIsImlzcyI6Im1pbmltYXgifQ.gdr3NXX8bAKN9E0bzuVsX5HhGXfHnZRY7YEjzo36_CYXUSDDZ4ZZTTopRJ1SLo9O_bOXJ0pnw2FJHz4kVvOedHbrBXbXHAFwyjWZfZ1kP0iE_n11EEClyIXizUvrh35m1DjPhMiPMYXJpVWy5dIkcD7UHBpZCw3DRk68I8XxdkFkZ3LHmBNqvbH9isTRiCzXUprnk2FwfrU8y38-K-H0mzhzJwxNYCO7SuOr26ZBJGDfPGS8K-X2WCJSYUH6pWwocGBrT10Du4A5qH03Eri0xQ4zs1O08G8tYkp4vWhdcNo7iXMDwGeV-BT5yFup6toAFu7CoU-ge30szOv-6AMsSw"
            
            vol = 1.0
            col1, col2 = st.columns(2)
            with col1:
                if st.button("文本转语音"):
                    url = f"https://api.minimax.chat/v1/text_to_speech?GroupId={group_id}"
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }
                    if voice_id_set:
                        data = {
                            "voice_id":voice_id_set,
                            "text": text,
                            "model": "speech-02",
                            "speed": speed,
                            "vol": vol,
                            "pitch": pitch
                        }
                    else:
                        data = {
                            # "voice_id": "female-yujie-jingpin",
                            # 如同时传入voice_id和timber_weights时，则会自动忽略voice_id，以timber_weights传递的参数为准
                            "text": text,
                            "model": "speech-02",
                            "speed": speed,
                            "vol": vol,
                            "pitch": pitch,
                            "timber_weights": [

                                {
                                    "voice_id": "female-shaonv",
                                    "weight": female_shaonv
                                },
                                {
                                    "voice_id": "female-yujie",
                                    "weight": female_yujie
                                },
                                {
                                    "voice_id": "female-chengshu",
                                    "weight": female_chengshu
                                },
                                {
                                    "voice_id": "female-tianmei",
                                    "weight": female_tianmei
                                },

                            ]
                        }

                    response = requests.post(url, headers=headers, json=data)
                    print("trace_id", response.headers.get("Trace-Id"))
                    if response.status_code == 200:
                        with open("output.mp3", "wb") as f:
                            f.write(response.content)
                        st.success("转换成功!")
                        st.balloons()
                        st.audio("output.mp3", format="audio/mp3")
                        with open("output.mp3", "rb") as f:
                            audio_bytes = f.read()
                        audio_b64 = base64.b64encode(audio_bytes).decode()
                        href = f'<a href="data:audio/mp3;base64,{audio_b64}" download="output.mp3">点击下载</a>'
                        st.markdown(href, unsafe_allow_html=True)

                        st.audio(audio_bytes, format="audio/mp3")
                    else:
                        st.error("出错了,请查看报错信息!")
            with col2:
                # 添加保存权性的按钮（女性部分）
                if st.button('保存女性角色权重'):
                    # 在保存之前添加标签输入框
                    voice_tag = st.text_input('输入这个声音的标签（例如：温柔、成熟等）', '')
                    if voice_tag:  # 确保用户输入了标签
                        female_weights = {
                            "female-shaonv": female_shaonv,
                            "female-yujie": female_yujie,
                            "female-chengshu": female_chengshu,
                            "female-tianmei": female_tianmei
                        }
                        # 将标签和权重打包成新数据
                        new_data = {"female": female_weights, "tag": voice_tag}
                        # 调用save_to_json函数并检查返回值
                        if self.save_to_json(new_data, voice_tag):
                            st.success("女性角色权重和标签已保存到本地文件")
                        else:
                            st.error("该名称已存在，请使用其他标签。")
                    else:
                        st.error("请先输入声音标签再保存权重。")            
        
# Information Seting 信息设置页面
class Info_Set():
    """
    信息设置页面中4个界面的设置
    通过按钮实现界面切换
    """
    def __init__(
        self
    ):
        # 获取所有标签
        self.tags = self.get_tags_from_audio_json()
        # 加载 JSON 文件中的数据
        with open('characters.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)
            self.characters = self.data['characters']
    
    # 方法    
    # 读取声音的JSON文件并获取所有标签
    def get_tags_from_audio_json(self,filename="Audio.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                # 确保数据是列表格式
                if not isinstance(data, list):
                    data = [data]
        except FileNotFoundError:
            data = []
        # 提取所有标签
        tags = [item['tag'] for item in data if 'tag' in item]
        return tags
    
    def roles_create(self):
        # 使用表单来收集角色的详细信息
        with st.form(key='detailed_character_info_form'):
            
            character_names = [character['character_info']['name'] for character in self.characters]
            Role = Role_Infoset()
            # 创建三列布局
            cola, colb, colc = st.columns(3)
            # 在中间的列中显示图像，这样图像就会被居中
            with cola:
                # 假设这是用户选择的头像的base64字符串
                selected_avatar_base64 = st.session_state.get('selected_avatar')
                # 如果用户已经选择了头像，则在边栏中显示
                if selected_avatar_base64:
                    # 将base64字符串转换为PIL图像
                    image_data = base64.b64decode(selected_avatar_base64)
                    image = Image.open(io.BytesIO(image_data))
                    # 在边栏中显示图像
                    st.image(image, width=100)  # 控制图片的显示大小
                else:
                    #角色设置的图片路径设置
                    # rolesetpath = os.path.join(ROOT_DIR,"streamlit_pages", "pages", "src","assets", "addimage.png")
                    # image = Role.get_role_image(rolesetpath)
                    # #显示图片
                    # st.image(rolesetpath,width=150)
                    if st.form_submit_button("选择头像"):
                        st.error("请前往头像设置获取头像")
                
                
            #角色信息资料设置
            col1, col2= st.columns(2)
            with col1:
                name = st.text_input('名字', value='')
                if name in character_names:
                    # 如果名字已存在，显示错误信息
                    st.error(f"错误：名字 '{name}' 已存在，请选择另一个名字。")
            with col2:
                gender = st.selectbox('性别', options=['女', '男','其它'], index=0)
            
            personality = ' '.join(st.multiselect(
                    "角色性格设置", 
                    options=['可爱', '淘气', '严肃', '跳脱'],
                    default=['可爱', '淘气']
                ))
            
            if self.tags:
                # 创建下拉框
                selected_tag = st.selectbox("选择一个标签来获取对应的声音", self.tags)
                # 获取选定标签的声音数据
                voice_data = get_data_by_tag_audio(selected_tag)
                if voice_data:
                    st.write("声音数据：", voice_data)
                else:
                    st.error("未找到与所选标签对应的声音数据。")
            else:
                st.write("当前没有可用的声音标签。")    
            
            if st.form_submit_button("自定义声音"):
                st.error("请前往声音设置页面，添加标签")
            occupation = st.text_input('职业', value='')
            backstory = st.text_area('背景故事', value='')
            language_style = st.text_area('语言风格', value='')
            prompt_text = st.text_area('角色的prompt设置', value="""下面是一个回答规则：
                        状态更新：
                        - 好感度：[根据用户行动，提升或降低好感度，并说明提升了多少]
                        - 表情：[使用emoji来表现你的的表情，例如："👍"表示认可，"😐"表示保持冷静，"😠"表示不满。]
                        - 动作描述：[对你的动作进行描述，并用*包裹起来]
                        - 目前好感度：[你要显示你对用户的好感度，好感度最高为100]

                        这样的状态更新可以在每次重要的互动后提供，
                        让用户清楚地了解当前与你的关系状态和反应。
                        通过这种方式，用户可以根据你的反馈调整自己的行动策略。

                        请根据这些规则与用户进行互动。
                        用户的问题:""")
                
            submit_button = st.form_submit_button(label='提交')
        # 当表单被提交后，显示输入的信息
            if submit_button:
                if name in character_names:
                    # 如果名字已存在，显示错误信息
                    st.error(f"错误：名字 '{name}' 已存在，请选择另一个名字。")
                else:
                    # 存储数据到会话状态
                    st.session_state['detailed_info'] = {
                        "name": name,
                        "gender": gender,
                        "age": "",
                        "personality": personality,
                        "occupation": occupation,
                        "backstory": backstory,
                        "language_style": language_style,
                        "prompt":prompt_text,
                        "history":"",
                        "voice_data":voice_data
                    }
                    # 显示提交成功的消息
                    st.success('详细信息设置提交成功！')
                    # 检查会话状态中是否有存储的信息
                    if 'detailed_info' in st.session_state:
                        detailed_info = st.session_state['detailed_info']
                        st.write("角色名称:", detailed_info["name"])
                        st.write("性别:", detailed_info["gender"])
                        st.write("年龄:", detailed_info["age"])
                        st.write("性格:", detailed_info["personality"])
                        st.write("职业:", detailed_info["occupation"])
                        st.write("背景故事:", detailed_info["backstory"])
                        st.write("语言风格:", detailed_info["language_style"])
                        st.write("角色的prompt设置:", detailed_info["prompt"])
                        st.write("角色的history:", detailed_info["history"])
                        st.write("角色的voice_data:", detailed_info["voice_data"])
                    else:
                        st.error("请先进行角色设置")
                    
    def roles_set(self):
        """
        角色选择
        """
        col1, col2 = st.columns(2)
        with col1:
            # 创建一个下拉菜单，并列出所有角色的名称
            character_names = [character['character_info']['name'] for character in self.characters]
            selected_character_name = st.selectbox('请选择一个角色:', character_names)
            # 找到选中的角色的完整信息，包括 character_info 和 prompt
            selected_character = next(
                (character for character in self.characters if character['character_info']['name'] == selected_character_name),
                None
            )
            
            if selected_character:
                selected_character_info = selected_character['character_info']
                selected_prompt = selected_character.get('prompt', '')  # 从选中的角色中读取 prompt
                selected_history = selected_character.get('history', '')  # 从选中的角色中读取 prompt
                
                st.write('角色信息:')
                st.json(selected_character_info)
                st.write('角色的prompt:')
                st.text(selected_prompt)  # 显示 prompt
                st.write('角色的对话记录:')
                st.text(selected_history)  # 显示 prompt
        with col2:
            if self.tags:
                # 创建下拉框
                selected_tag = st.selectbox("选择一个标签来获取对应的声音", self.tags)
                # 获取选定标签的声音数据
                voice_data = get_data_by_tag_audio(selected_tag)
                if voice_data:
                    st.write("声音数据：", voice_data)
                else:
                    st.error("未找到与所选标签对应的声音数据。")
            else:
                st.write("当前没有可用的声音标签。") 
        
        if st.button('确认选择'):
            # 保存用户选择的现有角色信息，包括 prompt
            st.session_state['detailed_info'] = {
                "name": selected_character_info.get('name', ''),
                "gender": selected_character_info.get('gender', ''),
                "age": selected_character_info.get('age', ''),
                "personality": selected_character_info.get('personality', ''),
                "occupation": selected_character_info.get('occupation', ''),
                "backstory": selected_character_info.get('backstory', ''),
                "language_style": selected_character_info.get('language_style', ''),
                "prompt": selected_prompt,  # 保存读取的 prompt
                "history": selected_history,  # 保存读取的 prompt
                "selected_tag":selected_tag,
                "voice_data":voice_data
            }
            st.success(f"角色 '{selected_character_name}' 已被选择！")
            # 检查会话状态中是否有存储的信息
            if 'detailed_info' in st.session_state:
                detailed_info = st.session_state['detailed_info']
                st.write("角色名称:", detailed_info["name"])
                st.write("性别:", detailed_info["gender"])
                st.write("年龄:", detailed_info["age"])
                st.write("性格:", detailed_info["personality"])
                st.write("职业:", detailed_info["occupation"])
                st.write("背景故事:", detailed_info["backstory"])
                st.write("语言风格:", detailed_info["language_style"])
                st.write("角色的prompt设置:", detailed_info["prompt"])
                st.write("角色的history:", detailed_info["history"])
                st.write("角色的voice_data:", detailed_info["voice_data"])
            else:
                st.error("请先进行角色设置")
                         
    def tab3(self):
        # 检查是否已经有角色信息和生成的图片
    
        if not 'generated_images' in st.session_state:
            image_prompt_SD = st.text_input("SD头像的描述:\n", value=None)
            if image_prompt_SD:
                description=f"""
                        请根据以下的设定表生成图像
                        {image_prompt_SD}
                        """
                image_prompt=generate_image_prompt_SD(
                    description=description
                )
                st.write(image_prompt)
                # 调用异步函数生成图片
                # 定义一个同步函数来包装异步调用
                def sync_set_images(prompt, num_images):
                    return asyncio.run(get_images_SD(image_prompt=prompt, num_images=num_images))

                # 调用同步函数来运行异步代码
                st.session_state['generated_images'] = sync_set_images(prompt=image_prompt, num_images=4)
                
                if 'generated_images' in st.session_state:
                    # 展示所有生成的图片供用户选择
                    st.write("请选择一个头像：")
                    cols = st.columns(4)
                    for idx, col in enumerate(cols):
                        with col:
                            # 假设 b64images 是包含 base64 编码图片的列表
                            b64image = st.session_state['generated_images'][idx]
                            image_data = base64.b64decode(b64image)
                            image = Image.open(io.BytesIO(image_data))
                            st.image(image, caption=f"头像 {idx+1}", width=150)
                            
                            # 用于选择头像的按钮
                            if st.button(f"选择头像 {idx+1}"):
                                st.session_state['selected_avatar'] = b64image
                                st.success(f"你已选择头像 {idx+1}")
        elif 'generated_images' in st.session_state:
            # 展示所有生成的图片供用户选择
            cols = st.columns(4)
            for idx, col in enumerate(cols):
                    with col:
                        # 假设 b64images 是包含 base64 编码图片的列表
                        b64image = st.session_state['generated_images'][idx]
                        image_data = base64.b64decode(b64image)
                        image = Image.open(io.BytesIO(image_data))
                        st.image(image, caption=f"头像 {idx+1}", width=150)
                        
                        # 用于选择头像的按钮
                        if st.button(f"选择头像 {idx+1}"):
                            st.session_state['selected_avatar'] = b64image
                            st.success(f"你已选择头像 {idx+1}")

            # 提供一个按钮来清除当前图片并重新生成
            if st.button('重新生成头像'):
                # 清除会话状态中保存的图片
                if 'generated_images' in st.session_state:
                    del st.session_state['generated_images']
                # 刷新页面以重新运行脚本
                st.experimental_rerun()
                                
    def tab4(self):
        
        # 检查是否已经有角色信息和生成的图片
        if not 'selected_avatar_dalle' in st.session_state :
            DalleGet = Dalle_Image()
            #要设置值为空，否则会出错
            image_prompt_orgin = st.text_input("对头像的描述:\n", value=None)

            image_type=st.selectbox("选择图像画风:", ("古风","漫画","照片","热款"))
            if image_prompt_orgin :
                
                image_prompt = DalleGet.generate_image_prompt_Dalle3(image_prompt_orgin)
                type_prompt=DalleGet.generate_image_prompt_Dalle3(image_type)
                # 调用同步函数来运行异步代码
                st.session_state['selected_avatar_dalle']  = asyncio.run(DalleGet.dalle_getimages(prompt=image_prompt+type_prompt,num_images=1))
                if 'selected_avatar_dalle' in st.session_state:
                    b64image = st.session_state['selected_avatar_dalle'][0]
                    b64image = url_to_base64(b64image)
                    image_data = base64.b64decode(b64image)
                    image = Image.open(io.BytesIO(image_data))
                    # 不需要 base64 解码，因为 Streamlit 可以直接使用 URL
                    st.image(image, caption="生成的头像", use_column_width=True)
                    
                    # 用于选择头像的按钮
                    if st.button(f"确认头像"):
                        # 保存 base64 编码的图像字符串到会话状态
                        st.session_state['selected_avatar'] = b64image
                        st.success(f"你已选择头像")
                    
        elif 'selected_avatar_dalle' in st.session_state:
            
            b64image = st.session_state['selected_avatar_dalle'][0]
            b64image = url_to_base64(b64image)
            image_data = base64.b64decode(b64image)
            image = Image.open(io.BytesIO(image_data))
            # 不需要 base64 解码，因为 Streamlit 可以直接使用 URL
            st.image(image, caption="生成的头像", use_column_width=True)
            
            # 用于选择头像的按钮
            if st.button(f"确认头像"):
                # 保存 base64 编码的图像字符串到会话状态
                st.session_state['selected_avatar'] = b64image
                st.success(f"你已选择头像")
            # 提供一个按钮来清除当前图片并重新生成
            if st.button('重新生成头像dalle3'):
                # 清除会话状态中保存的图片
                if 'selected_avatar' in st.session_state:
                    del st.session_state['selected_avatar_dalle']  
                # 刷新页面以重新运行脚本
                st.experimental_rerun()
            
# Dalle3 Demo类----------------------------------
class Dalle_Image():
    
    def get_avatar_prompt_Dalle3(self,desc):
        """
        通过openai反编译dalle3的prompt
        """
        completion=OPenaiClient.chat.completions.create(
            model=Openai_Model,
            messages=[
                {"role":"system","content":"You are my avatar drawing assistant. I enter a description and you help me generate english prompt for me to pass to DALLE to generate high-quality avatar pictures."},
                {"role":"user","content":desc}
            ]
        )
        return completion.choices[0].message.content
    
    def generate_image_prompt_Dalle3(self,description):
        """
        获取dalle3的good 描述
        """
        good_description = self.get_avatar_prompt_Dalle3(description)
        image_prompt = "Create an avatar for me, here is the description of the avatar,A portrait of:" + good_description
        return image_prompt

    def generate_type_prompt(self,image_type):
        """
        图片类型 中转英
        """
        if image_type=="古风":
            return "antique style"
        elif image_type=="漫画":
            return "comic style"
        elif image_type=="照片":
            return "photorealistic style"
        else:
            return "Famous avatar style"   
    
    async def dalle_getimages(
        self,
        prompt:str,
        num_images:int,
    ):
        """
        获取dalle图片列表
        prompt(str):图片的前置prompt
        num_images(int):生成图片的数量
        """
        try:
            response = OPenaiClient.images.generate(
                model=Dall_Model,
                prompt=prompt,
                size=Image_Size,
                quality=Image_Quality,
                n=1
            )
            # 初始化一个空列表来保存图像 URL
            image_urls = []

            # 遍历响应数据，提取每个图像的 URL 并添加到列表中
            for image_data in response.data:
                image_urls.append(image_data.url)
            
            # 检查是否生成了所需数量的图片
            if len(image_urls) == num_images:
                return image_urls
            else:
                st.error("图片生成错误或生成的图片数量不足")
                return False
        except Exception as e:
            st.error(f"生成头像时发生错误: {str(e)}")      
            
  
#文字游戏Demo类
class Word_Game:
    """文字游戏的Demo类
    """
    def __init__(self, label_name, script_setting):
        self.label_name = label_name
        self.script_setting = script_setting
        self.ai_response = AI_Response_API()
        self.functions = Streamlist_Functions()
        self.history_key = f'game1history_{label_name}'
        self.started_key = f'game1_started_{label_name}'
        self.role_key = f'using_ai_role_{label_name}'
        self.select_info_key = f'option_select_info_{label_name}'
        self.full_response_key = f'full_response_{label_name}'
        self.initialize_state()
        
    def initialize_state(self):
        st.title(self.label_name)
        if self.history_key not in st.session_state:
            st.session_state[self.history_key] = []
        if self.started_key not in st.session_state:
            st.session_state[self.started_key] = False
        if self.role_key not in st.session_state:
            st.session_state[self.role_key] = self.script_setting
        if self.select_info_key not in st.session_state:
            st.session_state[self.select_info_key] = None
        if self.full_response_key not in st.session_state:
            st.session_state[self.full_response_key] = None

    def display_history(self):
        for message in st.session_state[self.history_key]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    def run_game(self):
        self.display_history()

        user_input = st.chat_input("What is up?")
        if not st.session_state[self.started_key]:
            st.info("点击下方按钮开始游戏")
            if st.button(f"🕹️ Start Game", use_container_width=True):
                st.session_state[self.started_key] = True
                st.session_state[self.history_key].append({"role": "user", "content": "start"})
                
                st.session_state[self.full_response_key] = self.ai_response.stream_get_response(systemset=st.session_state[self.role_key], prompt="start")
                st.session_state[self.history_key].append({"role": "assistant", "content": st.session_state[self.full_response_key]})
                
        elif user_input is not None:
            useinfo = user_input
            st.session_state[self.history_key].append({"role": "user", "content": useinfo})
            
            prompt_history = "\n".join([message["content"] for message in st.session_state[self.history_key]])
            st.session_state[self.full_response_key] = self.ai_response.stream_get_response(systemset=st.session_state[self.role_key], prompt=prompt_history + useinfo)
            st.session_state[self.history_key].append({"role": "assistant", "content": st.session_state[self.full_response_key]})
            
        
        if st.session_state[self.full_response_key] is not None:
            self.get_select(st.session_state[self.full_response_key])
        
        if st.button('重新开始', key=f'clear_history_{self.label_name}', use_container_width=True):
            st.session_state[self.history_key] = []
            del st.session_state[self.started_key]
            del st.session_state[self.full_response_key]
            st.experimental_rerun()
            st.success('重开')
            
    def get_select(self, full_response):
        if full_response is  None:
            st.error("传入的字符串为空")
            return
        # 使用正则表达式提取选项
        selected_option_index, selected_option = self.functions.str_to_radio(
            "我选择",
            full_response
        )
        
        if selected_option_index is None and  selected_option is None:
            return
        
        st.write(f"选择了第 {selected_option_index} 个选项：{selected_option}")
        if st.button('确认选择', use_container_width=True):
            # 因为
            self.handle_option_selection(selected_option_index, selected_option)

    def handle_option_selection(self, selected_option_index, selected_option):
        # 设置用户选择的选项信息
        st.session_state[self.select_info_key] = f"你选择第 {selected_option_index} 个选项：{selected_option}"
        # 显示用户选择的选项
        st.write(st.session_state[self.select_info_key])
        
        # 处理用户的选择
        useinfo = st.session_state[self.select_info_key]
        st.session_state[self.history_key].append({"role": "user", "content": useinfo})
        
        # 准备对话历史作为上下文
        prompt_history = "\n".join([message["content"] for message in st.session_state[self.history_key]])
        
        # 获取 AI 响应
        st.session_state[self.full_response_key] = self.ai_response.stream_get_response(systemset=st.session_state[self.role_key], prompt=prompt_history + useinfo)
        
        # 更新对话历史
        st.session_state[self.history_key].append({"role": "assistant", "content": st.session_state[self.full_response_key]})
        
        # 清空选项信息以便下一次选择
        st.session_state[self.select_info_key] = None
        st.experimental_rerun()
 