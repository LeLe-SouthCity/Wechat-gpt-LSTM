import axios from 'axios';

const url = 'http://61.244.24.102/v1/chat-messages';
const headers = {
    'Authorization': 'Bearer app-QUUb1aNeslCUaPF1zsLynjqr',
    'Content-Type': 'application/json'
};
const data = {
    "inputs": {},
    "query": "你好",
    "response_mode": "blocking",
    "user": "le",
};

axios.post(url, data, { headers: headers })
  .then(response => {
    // 这里处理响应数据
    console.log(response.data);
  })
  .catch(error => {
    // 这里处理错误
    console.error(error);
  });
