import os
import streamlit as st
from openai import OpenAI as OpenAIDALLE
#Dalle3  参数
#获取openaikey
OpenAI_Key = st.secrets["openai"]["OPENAI_API_KEY"]

Image_Size ="1024x1792"  #图片大小
Image_Quality ="standard" #图片质量
# opeai cloent
OPenaiClient = OpenAIDALLE(
    api_key=OpenAI_Key
)

Dall_Model = "dall-e-3"

# Openai_Model = "gpt-3.5-turbo-0125"
Openai_Model = "gpt-4-0125-preview"


# SD的参数
stability_api_key = st.secrets["stability"]["STABILITY_API_KEY"]
Engine="stable-diffusion-xl-1024-v1-0"

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



