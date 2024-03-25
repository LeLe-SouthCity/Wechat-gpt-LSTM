import requests
import json

url = 'http://61.244.24.102/v1/chat-messages'
headers = {
    'Authorization': 'Bearer app-QUUb1aNeslCUaPF1zsLynjqr',
    'Content-Type': 'application/json'
}
data = {
    "inputs": {},
    "query": "今天星期几",
    "response_mode": "blocking",
    "user": "zha"
}

response = requests.post(url, headers=headers, data=json.dumps(data))

# 检查请求是否成功
if response.status_code == 200:
    print(response.json())  # 打印JSON响应内容
else:
    print(f"请求失败，状态码：{response.status_code}")
