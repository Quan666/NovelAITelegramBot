## Docker 安装

```bash
# 下载代码，进入代码目录
docker build -t aibot:latest .

#启动方式一
docker run -itd --name aibot aibot

#启动方式二（将容器挂载到代码目录 /root/NovelAITelegramBot/ 方便更新代码
docker run -itd -e TZ="Asia/Shanghai" -v "/root/NovelAITelegramBot:/app" --name aibot aibot
```

## 其他操作
```bash
# 重启
docker restart aibot
```
