from tts_configs import *
import wave
from enum import Enum
from hashlib import sha256
from io import BytesIO
from typing import List
from urllib.parse import urlparse
import time
import websockets
import streamlit as st
from tts_configs import * 





def generate_header(
    version=PROTOCOL_VERSION,
    message_type=CLIENT_FULL_REQUEST,
    message_type_specific_flags=NO_SEQUENCE,
    serial_method=JSON,
    compression_type=GZIP,
    reserved_data=0x00,
    extension_header=bytes()
):
    """
    protocol_version(4 bits), header_size(4 bits),
    message_type(4 bits), message_type_specific_flags(4 bits)
    serialization_method(4 bits) message_compression(4 bits)
    reserved （8bits) 保留字段
    header_extensions 扩展头(大小等于 8 * 4 * (header_size - 1) )
    """
    header = bytearray()
    header_size = int(len(extension_header) / 4) + 1
    header.append((version << 4) | header_size)
    header.append((message_type << 4) | message_type_specific_flags)
    header.append((serial_method << 4) | compression_type)
    header.append(reserved_data)
    header.extend(extension_header)
    return header


def generate_full_default_header():
    return generate_header()


def generate_audio_default_header():
    return generate_header(
        message_type=CLIENT_AUDIO_ONLY_REQUEST
    )


def generate_last_audio_default_header():
    return generate_header(
        message_type=CLIENT_AUDIO_ONLY_REQUEST,
        message_type_specific_flags=NEG_SEQUENCE
    )

def parse_response(res):
    """
    protocol_version(4 bits), header_size(4 bits),
    message_type(4 bits), message_type_specific_flags(4 bits)
    serialization_method(4 bits) message_compression(4 bits)
    reserved （8bits) 保留字段
    header_extensions 扩展头(大小等于 8 * 4 * (header_size - 1) )
    payload 类似与http 请求体
    """
    protocol_version = res[0] >> 4
    header_size = res[0] & 0x0f
    message_type = res[1] >> 4
    message_type_specific_flags = res[1] & 0x0f
    serialization_method = res[2] >> 4
    message_compression = res[2] & 0x0f
    reserved = res[3]
    header_extensions = res[4:header_size * 4]
    payload = res[header_size * 4:]
    result = {}
    payload_msg = None
    payload_size = 0
    if message_type == SERVER_FULL_RESPONSE:
        payload_size = int.from_bytes(payload[:4], "big", signed=True)
        payload_msg = payload[4:]
    elif message_type == SERVER_ACK:
        seq = int.from_bytes(payload[:4], "big", signed=True)
        result['seq'] = seq
        if len(payload) >= 8:
            payload_size = int.from_bytes(payload[4:8], "big", signed=False)
            payload_msg = payload[8:]
    elif message_type == SERVER_ERROR_RESPONSE:
        code = int.from_bytes(payload[:4], "big", signed=False)
        result['code'] = code
        payload_size = int.from_bytes(payload[4:8], "big", signed=False)
        payload_msg = payload[8:]
    if payload_msg is None:
        return result
    if message_compression == GZIP:
        payload_msg = gzip.decompress(payload_msg)
    if serialization_method == JSON:
        payload_msg = json.loads(str(payload_msg, "utf-8"))
    elif serialization_method != NO_SERIALIZATION:
        payload_msg = str(payload_msg, "utf-8")
    result['payload_msg'] = payload_msg
    result['payload_size'] = payload_size
    return result

def read_wav_info(data: bytes = None) -> (int, int, int, int, int):
    with BytesIO(data) as _f:
        wave_fp = wave.open(_f, 'rb')
        nchannels, sampwidth, framerate, nframes = wave_fp.getparams()[:4]
        wave_bytes = wave_fp.readframes(nframes)
    return nchannels, sampwidth, framerate, nframes, len(wave_bytes)

class AudioType(Enum):
    LOCAL = 1  # 使用本地音频文件

class AsrWsClient:
    def __init__(self, audio_path, cluster, **kwargs):
        """
        :param config: config
        """
        self.audio_path = audio_path
        self.cluster = cluster
        self.success_code = 1000  # success code, default is 1000
        self.seg_duration = int(kwargs.get("seg_duration", 15000))
        self.nbest = int(kwargs.get("nbest", 1))
        self.appid = kwargs.get("appid", "")
        self.token = kwargs.get("token", "")
        self.ws_url = kwargs.get("ws_url", "wss://openspeech.bytedance.com/api/v2/asr")
        self.uid = kwargs.get("uid", "streaming_asr_demo")
        self.workflow = kwargs.get("workflow", "audio_in,resample,partition,vad,fe,decode,itn,nlu_punctuate")
        self.show_language = kwargs.get("show_language", False)
        self.show_utterances = kwargs.get("show_utterances", False)
        self.result_type = kwargs.get("result_type", "full")
        self.format = kwargs.get("format", "wav")
        self.rate = kwargs.get("sample_rate", 16000)
        self.language = kwargs.get("language", "zh-CN")
        self.bits = kwargs.get("bits", 16)
        self.channel = kwargs.get("channel", 1)
        self.codec = kwargs.get("codec", "raw")
        self.audio_type = kwargs.get("audio_type", AudioType.LOCAL)
        self.secret = kwargs.get("secret", "access_secret")
        self.auth_method = kwargs.get("auth_method", "token")
        self.mp3_seg_size = int(kwargs.get("mp3_seg_size", 10000))

    def construct_request(self, reqid):
        req = {
            'app': {
                'appid': self.appid,
                'cluster': self.cluster,
                'token': self.token,
            },
            'user': {
                'uid': self.uid
            },
            'request': {
                'reqid': reqid,
                'nbest': self.nbest,
                'workflow': self.workflow,
                'show_language': self.show_language,
                'show_utterances': self.show_utterances,
                'result_type': self.result_type,
                "sequence": 1
            },
            'audio': {
                'format': self.format,
                'rate': self.rate,
                'language': self.language,
                'bits': self.bits,
                'channel': self.channel,
                'codec': self.codec
            }
        }
        return req

    @staticmethod
    def slice_data(data: bytes, chunk_size: int) -> (list, bool):
        """
        slice data
        :param data: wav data
        :param chunk_size: the segment size in one request
        :return: segment data, last flag
        """
        data_len = len(data)
        offset = 0
        while offset + chunk_size < data_len:
            yield data[offset: offset + chunk_size], False
            offset += chunk_size
        else:
            yield data[offset: data_len], True

    def _real_processor(self, request_params: dict) -> dict:
        pass

    def token_auth(self):
        return {'Authorization': 'Bearer; {}'.format(self.token)}

    def signature_auth(self, data):
        header_dicts = {
            'Custom': 'auth_custom',
        }

        url_parse = urlparse(self.ws_url)
        input_str = 'GET {} HTTP/1.1\n'.format(url_parse.path)
        auth_headers = 'Custom'
        for header in auth_headers.split(','):
            input_str += '{}\n'.format(header_dicts[header])
        input_data = bytearray(input_str, 'utf-8')
        input_data += data
        mac = base64.urlsafe_b64encode(
            hmac.new(self.secret.encode('utf-8'), input_data, digestmod=sha256).digest())
        header_dicts['Authorization'] = 'HMAC256; access_token="{}"; mac="{}"; h="{}"'.format(self.token,
                                                                                              str(mac, 'utf-8'), auth_headers)
        return header_dicts

    async def segment_data_processor(self, wav_data: bytes, segment_size: int):
        reqid = str(uuid.uuid4())
        # 构建 full client request，并序列化压缩
        request_params = self.construct_request(reqid)
        payload_bytes = str.encode(json.dumps(request_params))
        payload_bytes = gzip.compress(payload_bytes)
        full_client_request = bytearray(generate_full_default_header())
        full_client_request.extend((len(payload_bytes)).to_bytes(4, 'big'))  # payload size(4 bytes)
        full_client_request.extend(payload_bytes)  # payload
        header = None
        if self.auth_method == "token":
            header = self.token_auth()
        elif self.auth_method == "signature":
            header = self.signature_auth(full_client_request)
        async with websockets.connect(self.ws_url, extra_headers=header, max_size=1000000000) as ws:
            # 发送 full client request
            await ws.send(full_client_request)
            res = await ws.recv()
            result = parse_response(res)
            if 'payload_msg' in result and result['payload_msg']['code'] != self.success_code:
                return result
            for seq, (chunk, last) in enumerate(AsrWsClient.slice_data(wav_data, segment_size), 1):
                # if no compression, comment this line
                payload_bytes = gzip.compress(chunk)
                audio_only_request = bytearray(generate_audio_default_header())
                if last:
                    audio_only_request = bytearray(generate_last_audio_default_header())
                audio_only_request.extend((len(payload_bytes)).to_bytes(4, 'big'))  # payload size(4 bytes)
                audio_only_request.extend(payload_bytes)  # payload
                # 发送 audio-only client request
                await ws.send(audio_only_request)
                res = await ws.recv()
                result = parse_response(res)
                if 'payload_msg' in result and result['payload_msg']['code'] != self.success_code:
                    return result
        return result

    async def execute(self):
        with open(self.audio_path, mode="rb") as _f:
            data = _f.read()
        audio_data = bytes(data)
        if self.format == "mp3":
            segment_size = self.mp3_seg_size
            return await self.segment_data_processor(audio_data, segment_size)
        if self.format != "wav":
            raise Exception("format should in wav or mp3")
        nchannels, sampwidth, framerate, nframes, wav_len = read_wav_info(
            audio_data)
        size_per_sec = nchannels * sampwidth * framerate
        segment_size = int(size_per_sec * self.seg_duration / 1000)
        return await self.segment_data_processor(audio_data, segment_size)

def execute_one(audio_item, cluster, **kwargs):
    """

    :param audio_item: {"id": xxx, "path": "xxx"}
    :param cluster:集群名称
    :return:
    """
    assert 'id' in audio_item
    assert 'path' in audio_item
    audio_id = audio_item['id']
    audio_path = audio_item['path']
    audio_type = AudioType.LOCAL
    asr_http_client = AsrWsClient(
        audio_path=audio_path,
        cluster=cluster,
        audio_type=audio_type,
        **kwargs
    )
    result = asyncio.run(asr_http_client.execute())
    return {"id": audio_id, "path": audio_path, "result": result}


# 提取json字段中的解析数据
def extract_text(data):
    # 检查所需的键是否存在于字典中
    if 'result' in data and \
    'payload_msg' in data['result'] and \
    'result' in data['result']['payload_msg']:
        # 获取result列表
        results = data['result']['payload_msg']['result']
        # 检查列表中是否有元素
        if results and isinstance(results, list):
            # 提取第一个元素中的text字段
            text = results[0].get('text', None)
            return text
    return None  # 如果任何键不存在，返回None

def audio_2_txt(
    path,
    audio_format="mp3",
    appid :str = "9268639668",
    access_token:str = "EWHAC-wfqVyyV43urNNRAKvR-6ZCQ0b1",
    cluster :str = "volcengine_streaming_common",
    ):
    result = execute_one(
        {
            'id': 1,
            'path': path
        },
        cluster=cluster,
        appid=appid,
        token=access_token,
        format=audio_format,
    )
    
    # 使用函数提取"text"
    result = extract_text(result)
    return result


#-----------------------------------以上全是官网示例
class Tts_Utils_Set():
    
    # 提取json字段中的解析数据
    def extract_text(self,data):
        # 检查所需的键是否存在于字典中
        if 'result' in data and \
        'payload_msg' in data['result'] and \
        'result' in data['result']['payload_msg']:
            # 获取result列表
            results = data['result']['payload_msg']['result']
            # 检查列表中是否有元素
            if results and isinstance(results, list):
                # 提取第一个元素中的text字段
                text = results[0].get('text', None)
                return text
        return None  # 如果任何键不存在，返回None

    
   
    # 填写平台申请的appid, access_token以及cluster
    async def get_and_save_requests(
        self,
        voice_type:str,
        save_path:str,
        text:str,
        encoding:str="mp3",
        appid :str = "8327388829",
        access_token:str = "OqJcUzMQpZauOEDFHnqxulIl0CxFHufD",
        cluster :str = "volcano_tts",
        ):
        
        voice_type = voice_type
        host = "openspeech.bytedance.com"
        api_url = f"https://{host}/api/v1/tts"

        header = {"Authorization": f"Bearer;{access_token}"}

        request_json = {
            "app": {
                "appid": appid,
                "token": "access_token",
                "cluster": cluster
            },
            "user": {
                "uid": "388808087185088"
            },
            "audio": {
                "voice_type": voice_type,
                "encoding": encoding,
                "speed_ratio": 1.0,
                "volume_ratio": 1.0,
                "pitch_ratio": 1.0,
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "text_type": "plain",
                "operation": "query",
                "with_frontend": 1,
                "frontend_type": "unitTson"

            }
        }
        try:
            resp = requests.post(api_url, json.dumps(request_json), headers=header)
            print(f"resp body: \n{resp.json()}")
            if "data" in resp.json():
                data = resp.json()["data"]
                file_to_save = open(save_path, "wb")
                file_to_save.write(base64.b64decode(data))
        except Exception as e:
            e.with_traceback() 

    # Streamlit应用
    def select_vioice_type(self):
        # 读取JSON文件
        with open('voices.json', 'r', encoding='utf-8') as f:
            voices_data = json.load(f)

        # 选择语言
        languages = list(voices_data.keys())
        selected_language = st.sidebar.selectbox('选择语言', languages)
        st.session_state['selected_language'] = selected_language
        if selected_language:
            # 选择场景
            scenes = list(voices_data[selected_language].keys())
            selected_scene = st.sidebar.selectbox('选择场景', scenes)
            st.session_state['selected_scene'] = selected_scene

            if selected_scene:
                # 选择音色名称和voice_type
                voice_options = voices_data[selected_language][selected_scene]
                voice_names = [voice['音色名称'] for voice in voice_options]
                selected_voice_name = st.sidebar.selectbox('选择音色名称', voice_names)
                st.session_state['selected_voice_name'] = selected_voice_name

                if selected_voice_name:
                    # 显示选中的voice_type
                    selected_voice = next(voice for voice in voice_options if voice['音色名称'] == selected_voice_name)
                    st.session_state['selected_voice'] = selected_voice['voice_type']
                    return st.session_state['selected_voice']
        return None

