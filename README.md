# 企微GPT-with LSTM/dify/openai

![小O同学实例](WeWork-OpenAI-Node/Image/image1.png)



## 🌟 项目特点

- 完成面向企业应用场景，
- 一键部署，Serverless 无服务器模式，
- 向导式安装，文档详细，安全可靠，网络延迟小,速度快


## 部署方法

<details>
    <summary>服务器部署</summary>
<br>
1. 创建企业微信应用<br>

第一步，创建应用，操作方法：企微管理员， 电脑端上的企业微信-->头像-->管理企业-->应用管理-->（最下面）创建应用-->应用logo + 填入基本信息

![image](https://user-images.githubusercontent.com/12178686/233253399-489b0905-9a4c-4b2e-8f5d-ed7e8dac0f6b.png)


第二步，配置应用，操作方法：接收消息一栏-->设置API接收-->未完等待第四步。
![image](https://user-images.githubusercontent.com/12178686/233256124-cc6334e3-90ff-43e7-8fe5-3dc0026226fb.png)

第三步，记录和准备下列字段信息， **corpid, agentid, secret, token ,aeskey, open-api-key**

**corpid** :  电脑端上的企业微信-->头像-->管理企业-->我的企业（下方） 图略<br/><br/>
**agentid, secret**: 第一步里完成后可见。
![image](https://user-images.githubusercontent.com/12178686/233275423-67281448-02ee-4e61-8586-0fe095351fb2.png)

**token ,aeskey**： 在设置API接收里（上面第二步）

**open-api-key**
这个需要在ChatGPT账号里生成，（如果没有chatgpt 账号也可以让别人生成一个，但是这个会产生费用） 
![image](https://user-images.githubusercontent.com/12178686/233278134-9d3fb914-9f3a-4049-b20e-3b0f237239f6.png)

[申请网址API KEY](https://platform.openai.com/account/api-keys)


运行下面命令
```
pip install -r requirements.txt (如果不行就一个一个运行)
pip install nodejs (版本大于1.18)
npm install 

#(LSTM + 微调gpt)
nohup python /home/ubuntu/WeWork-OpenAI-Node/AI-npc-demo/Streamlis_Demos/victor_Demo/vectorflask.py & 
#(微调gpt)
nohup python /home/ubuntu/WeWork-OpenAI-Node/flaskopenaiog.py & 
nohup node app.js &
```

flask 测试
```
curl -X POST -H "Content-Type: application/json" -d '{"user_input": "What do you know about me?"}' http://localhost:5000/chat

```

## 将服务器的ip地址配置到可信IP里，至此所有配置工作完成。下面就可以直接体验了，手机或电脑上企业微信进入自己创建的应用，可以和ChatGPT的聊起来了。 

</details>

<details>
    <summary>云函数部署</summary>
<br>
1. 创建企业微信应用<br>

第一步，创建应用，操作方法：企微管理员， 电脑端上的企业微信-->头像-->管理企业-->应用管理-->（最下面）创建应用-->应用logo + 填入基本信息

![image](https://user-images.githubusercontent.com/12178686/233253399-489b0905-9a4c-4b2e-8f5d-ed7e8dac0f6b.png)


第二步，配置应用，操作方法：接收消息一栏-->设置API接收-->未完等待第四步。
![image](https://user-images.githubusercontent.com/12178686/233256124-cc6334e3-90ff-43e7-8fe5-3dc0026226fb.png)

第三步，记录和准备下列字段信息， **corpid, agentid, secret, token ,aeskey, open-api-key**

**corpid** :  电脑端上的企业微信-->头像-->管理企业-->我的企业（下方） 图略<br/><br/>
**agentid, secret**: 第一步里完成后可见。
![image](https://user-images.githubusercontent.com/12178686/233275423-67281448-02ee-4e61-8586-0fe095351fb2.png)

**token ,aeskey**： 在设置API接收里（上面第二步）

**open-api-key**
这个需要在ChatGPT账号里生成，（如果没有chatgpt 账号也可以让别人生成一个，但是这个会产生费用） 
![image](https://user-images.githubusercontent.com/12178686/233278134-9d3fb914-9f3a-4049-b20e-3b0f237239f6.png)

[申请网址API KEY](https://platform.openai.com/account/api-keys)


第四步，一键部署到Render（代理服务器，免费，可以升级付费） 
<a href="https://render.com/deploy?repo=https://github.com/sytpb/chatgpt-wework-robot">
  <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render">
</a>

![image](https://user-images.githubusercontent.com/12178686/233276472-77ad1f07-e275-4bc2-a0fa-1c7d0b7172bc.png)

如图所示，将上面的字段信息填入，然后点击Apply。 


需要等3-5分钟部署，完成后复制生成的服务的URL，如下图，**然后拷贝URL后面拼接上/message**, 比如URL是 https://abc.com 拼接成 https://abc.com/message， 粘贴到上面**第二步**页面里，然后点保存，看到提示类似”保存成功“，代表服务已经配置成功了！
![image](https://user-images.githubusercontent.com/12178686/233277321-5392207b-58c5-4c6e-959e-de71518e4094.png)

最后一步： 企业可信IP配置， 应用页的最下方，配置可信IP。 
![image](https://user-images.githubusercontent.com/12178686/233280128-10dbcbdd-db47-47d2-91a0-8b20f2fd8893.png)

IP地址如下图，Render->Connect->Outbound 
![image](https://user-images.githubusercontent.com/12178686/233280575-8d92c978-cf06-4763-9443-694f495d3e16.png)

将这三个ip地址配置到可信IP里，至此所有配置工作完成。
<br/>

:100: 下面就可以直接体验了，手机或电脑上企业微信进入自己创建的应用，可以和ChatGPT的聊起来了。 
</details>

<details>
<summary>服务器docker部署</summary>


1. 相较于**云函数部署**方案，该方案需要:
    - 一台服务器
    - 一个域名

1. 创建企业微信应用（参考`云函数部署 1.创建企业微信应用 第一、二、三步`）

1. 复制变量文件 `.env.example`，填写自己的配置

    - 若服务器网络与openai api不能直连，可配置自定义 openai api 地址，`OPENAI_PROXY_URL`.  
      若无需自定义，请留空.
        ```yaml
        OPENAI_PROXY_URL=openai.abc.com
        ```

1. 运行docker

    假设新变量文件名为 `.env.local`

    ```bash
    # docker4bill/ww-openai-node:alpine 为构建好的镜像，你也可以利用本仓库的 Dockerfile 构建自己的镜像
    docker run --env-file .env.local -p 6060:6060 -d docker4bill/ww-openai-node:alpine
    ```

1. 用 `caddy` 或者 `nginx` 给以上服务做个反代

    假设域名是**abc.com**, 以`caddy`为例配置:

    ```yaml
    abc.com {
      reverse_proxy localhost:6060
    }
    ```

1. 将服务器IP添加到**企业可信IP**

1. 填写**接收消息服务器配置 URL**

    假设反代地址为`abc.com`，在**其后添加/message**，将地址`https://abc.com/message`填入接收消息服务器配置的URL里
</details>
