# 目前共有3个分支

# AI-npc-demo-streamlit

AI-npc-demo 是一个用于开发人工智能非玩家角色（AINPC）的项目。
它利用Langchain库提供强大的交互式接口，使得NPC的开发更加直观和便捷。

## Code文件夹
此文件夹包含langchain方面的所有代码
## Streamlis_Demos文件夹
此文件夹包含streamlit——所有Demo代码
## Source文件夹
一些用于测试AI-NPC的角色pdf与向量化保存路径

## 配置文件
- `environment.yml`：包含创建项目虚拟环境所需的所有配置信息。
- `requirements.txt`：列出了项目所需的所有Python依赖及其版本。

# 环境配置
## miniconda 安装
```bash
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh

~/miniconda3/bin/conda init bash
~/miniconda3/bin/conda init zsh

```
我们建议在一个虚拟环境下进行实验
1、创建项目的虚拟环境，请确保您已经安装了[conda](https://docs.conda.io/en/latest/)，然后运行以下命令：

```bash
conda env create -f environment.yml
```

这将根据`environment.yml`文件中定义的配置创建一个新的虚拟环境。

2、启动环境

```bash
conda activate langchain2
```

## 如果python需要安装依赖

2、在虚拟环境中，您可以通过以下命令安装所有必要的Python依赖：

```bash
pip install -r requirements.txt
```

这将根据`requirements.txt`文件安装所需的依赖包。

## 运行应用
或者您可以通过下面的命令启动streamlit 来启动streamlit

```bash
streamlit run app.py
```
你可以用下面的方式来指定开放的IP
```bash
streamlit run your_script.py --server.address 0.0.0.0 --server.port 8501
```

--server.address 0.0.0.0 指示Streamlit侦听所有网络接口。
--server.port 8501 可以更改为其他端口，如果您希望应用在不同的端口上运行

通过一个网页来与langchain进行实时交互




# nginx 配置（如果需要）

1、首先，更新你的包索引：
```bash
sudo apt update
```

2、然后，安装Nginx：

```bash
sudo apt install nginx
```

3、完成安装后，启动Nginx服务：

```bash
sudo systemctl start nginx
```

4、确保Nginx在启动时自动运行：

```bash
sudo systemctl enable nginx
```

5、进入nginx配置文件
```bash
cd  /etc/nginx/sites-enabled

sudo vim streamlit
```
```bash
server {
    listen 443 ssl;
    server_name audio.keith.com;  # 更改为您的域名

    ssl_certificate /home/ubuntu/AI-NPC/AI-npc-demo-main/urlKey/audio.keithhe.com.pem;  # 指向您的 SSL 证书文件
    ssl_certificate_key /home/ubuntu/AI-NPC/AI-npc-demo-main/urlKey/audio.keithhe.com.key;  # 指向您的私钥文件

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://localhost:8501;  # 假设 Streamlit 运行在 8501端口
        proxy_http_version 1.1;
        proxy_set_header Host $http_host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}



# 重定向 HTTP 到 HTTPS
server {
    listen 80;
    server_name audio.keithhe.com ;

    location / {
        return 301 https://$host$request_uri;
    }
}
```


6、 设置为可运行文件
```bash
sudo chmod 777  streamlit
```
7、重新加载文件
```bash

sudo nginx -s reload
```
## 联系方式

如果您有任何问题或需要帮助，请联系<848787675@qq.com>。
```
