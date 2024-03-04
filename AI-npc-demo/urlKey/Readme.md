# nginx 下载

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