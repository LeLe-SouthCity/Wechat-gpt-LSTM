import streamlit as st
import os
import sys
import base64
import time
import io
import json
import uuid
import requests
import datetime
import asyncio
import hmac
import gzip
import logging
import wave
import websockets
from PIL import Image
from enum import Enum
from hashlib import sha256
from io import BytesIO
from typing import List
from urllib.parse import urlparse

# tts config audio2txt 流式语音识别 #录音文件识别
Tts_stream_a2t_appid = "9268639668"    # 项目的 appid
Tts_stream_a2t_token = "EWHAC-wfqVyyV43urNNRAKvR-6ZCQ0b1"    # 项目的 token
Tts_stream_a2t_cluster = "volcengine_streaming_common"  # 请求的集群



PROTOCOL_VERSION = 0b0001
DEFAULT_HEADER_SIZE = 0b0001

PROTOCOL_VERSION_BITS = 4
HEADER_BITS = 4
MESSAGE_TYPE_BITS = 4
MESSAGE_TYPE_SPECIFIC_FLAGS_BITS = 4
MESSAGE_SERIALIZATION_BITS = 4
MESSAGE_COMPRESSION_BITS = 4
RESERVED_BITS = 8

# Message Type:
CLIENT_FULL_REQUEST = 0b0001
CLIENT_AUDIO_ONLY_REQUEST = 0b0010
SERVER_FULL_RESPONSE = 0b1001
SERVER_ACK = 0b1011
SERVER_ERROR_RESPONSE = 0b1111

# Message Type Specific Flags
NO_SEQUENCE = 0b0000  # no check sequence
POS_SEQUENCE = 0b0001
NEG_SEQUENCE = 0b0010
NEG_SEQUENCE_1 = 0b0011

# Message Serialization
NO_SERIALIZATION = 0b0000
JSON = 0b0001
THRIFT = 0b0011
CUSTOM_TYPE = 0b1111

# Message Compression
NO_COMPRESSION = 0b0000
GZIP = 0b0001
CUSTOM_COMPRESSION = 0b1111

services_Cluster_ID = {
    "流式语音识别-办公-中文": {
        "用量限额": "20.00 小时",
        "并发限额": 3,
        "Cluster ID": "volcengine_streaming",
    },
    "流式语音识别-办公-英文": {
        "用量限额": "20.00 小时",
        "并发限额": 3,
        "Cluster ID": "volcengine_streaming_en",
    },
    "流式语音识别-办公-日语": {
        "用量限额": "20.00 小时",
        "并发限额": 3,
        "Cluster ID": "volcengine_streaming_ja",
    },
    "流式语音识别-办公-韩语": {
        "用量限额": "20.00 小时",
        "并发限额": 3,
        "Cluster ID": "volcengine_streaming_ko",
    },
    "流式语音识别-办公-法语": {
        "用量限额": "20.00 小时",
        "并发限额": 3,
        "Cluster ID": "volcengine_streaming_fr_fr",
    },
    "流式语音识别-办公-西班牙语": {
        "用量限额": "20.00 小时",
        "并发限额": 3,
        "Cluster ID": "volcengine_streaming_es_mx",
    },
    "流式语音识别-办公-葡萄牙语": {
        "用量限额": "20.00 小时",
        "并发限额": 3,
        "Cluster ID": "volcengine_streaming_pt_br",
    },
    "流式语音识别-办公-印尼语": {
        "用量限额": "20.00 小时",
        "并发限额": 3,
        "Cluster ID": "volcengine_streaming_id",
    },
    "流式语音识别-办公-俄语": {
        "用量限额": "20.00 小时",
        "并发限额": 3,
        "Cluster ID": "volcengine_streaming_ru",
    },
    "流式语音识别-办公-马来语": {
        "用量限额": "20.00 小时",
        "并发限额": 3,
        "Cluster ID": "volcengine_streaming_ms",
    }
}

# 使用示例
# for service_name, details in services.items():
#     print(f"服务名称: {service_name}")
#     for key, value in details.items():
#         print(f"{key}: {value}")
#     print()  # 为了更好的可读性，每个服务的信息后面加一个空行
