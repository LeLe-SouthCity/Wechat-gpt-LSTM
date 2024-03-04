
import argparse
from typing import List
from typing import Union
# [START speech_transcribe_model_selection_v2]
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech


class Google_API_Get():
    
    def __init__(
        self,
        project_id: Union[str, None] ,
        model: Union[str, None] ,
        language_codes: Union[List[str], None],
        *args, 
        **kwargs
    ):
        """Google api  设置
    

        Args:
            project_id (str): 项目的ID编号
            model (str): 模型的选择 
            language_codes(List[str]):选择的语言类型
        """
        #如果设置了项目ID
        if project_id:
            self.project_id = project_id
        else:
            self.project_id = "enhanced-burner-413002"
        #如果设置了模型 
        if model:
            self.model = model
        else:
            self.model = "short"
        #如果选择了语言
        if language_codes:
            self.language_codes = language_codes
        else:
            self.language_codes = ["en-US"]
            
        
        
        
    
    def transcribe_model_selection_v2(
        self,
        audio_file: str,
    ) -> cloud_speech.RecognizeResponse:
        """Google api  将本地audio文件翻译成文本

        Args:
            language_codes (List[str]): 选择的语言列表
            audio_file (str): 语音文件路径
            
        Returns:
            (str): 返回翻译后的回复
        """
        # Instantiates a client
        client = SpeechClient()

        # Reads a file as bytes
        with open(audio_file, "rb") as f:
            content = f.read()

        config = cloud_speech.RecognitionConfig(
            auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
            language_codes=self.language_codes,
            model=self.model,
            features=cloud_speech.RecognitionFeatures(
                enable_automatic_punctuation=True,
            )
        )

        request = cloud_speech.RecognizeRequest(
            recognizer=f"projects/{self.project_id}/locations/global/recognizers/_",
            config=config,
            content=content,
        )

        # Transcribes the audio into text
        response = client.recognize(request=request)

        for result in response.results:
            res = result.alternatives[0].transcript
            print(f"Transcript: {result.alternatives[0].transcript}")
            return res

        return response


def get_bcp47():
        """返回两个东西
        Returns:
            bcp_47_codes(list[str]): 返回short 模型对应的可选语言代码
            language_to_country:(dict[str, str]):返回BCP-47语言代码到国家或地区的映射
        """
        
        # BCP-47语言代码到国家或地区的映射
        language_to_country = {
            "en-US": "英语（美国）","ja-JP": "日语（日本）","en-IN": "英语（印度）","en-GB": "英语（英国）",
            "hi-IN": "印地语（印度）", "en-AU": "英语（澳大利亚）","ar-DZ": "阿拉伯语（阿尔及利亚）",
            "ar-BH": "阿拉伯语（巴林）", "ar-EG": "阿拉伯语（埃及）", "ar-IQ": "阿拉伯语（伊拉克）","ar-IL": "阿拉伯语（以色列）",
            "ar-JO": "阿拉伯语（约旦）", "ar-KW": "阿拉伯语（科威特）","ar-LB": "阿拉伯语（黎巴嫩）","ar-MR": "阿拉伯语（毛里塔尼亚）", 
            "ar-MA": "阿拉伯语（摩洛哥）", "ar-OM": "阿拉伯语（阿曼）","ar-QA": "阿拉伯语（卡塔尔）","ar-SA": "阿拉伯语（沙特阿拉伯）",  
            "ar-PS": "阿拉伯语（巴勒斯坦）","ar-TN": "阿拉伯语（突尼斯）", "ar-AE": "阿拉伯语（阿联酋）", "ar-YE": "阿拉伯语（也门）", "da-DK": "丹麦语（丹麦）",
            "nl-NL": "荷兰语（荷兰）","fi-FI": "芬兰语（芬兰）", "fr-CA": "法语（加拿大）","fr-FR": "法语（法国）", "de-DE": "德语（德国）", "id-ID": "印尼语（印尼）",
            "it-IT": "意大利语（意大利）","ko-KR": "韩语（韩国）", "mk-MK": "马其顿语（北马其顿）",
            "no-NO": "挪威语（挪威）", "pl-PL": "波兰语（波兰）", "pt-BR": "葡萄牙语（巴西）","pt-PT": "葡萄牙语（葡萄牙）",
            "ro-RO": "罗马尼亚语（罗马尼亚）","ru-RU": "俄语（俄罗斯）", "es-CO": "西班牙语（哥伦比亚）","es-MX": "西班牙语（墨西哥）","es-ES": "西班牙语（西班牙）",
            "es-US": "西班牙语（美国）","th-TH": "泰语（泰国）","tr-TR": "土耳其语（土耳其）","uk-UA": "乌克兰语（乌克兰）",
            "vi-VN": "越南语（越南）","en-CA": "英语（加拿大）"
        }
        return language_to_country
    