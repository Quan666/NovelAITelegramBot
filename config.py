import httpx

# 去这注册 https://my.telegram.org/auth?to=apps
API_ID = 1234567
API_HASH = ""

# 去这注册 https://t.me/botfather
BOT_TOKEN = ""

# 原版后端地址
ai_api_url = "http://1.1.1.1/generate-stream"


# httpx_proxy = httpx.Proxy(
#     url="http://127.0.0.1:7890",
# )
httpx_proxy = {}

# bot_proxy = ("http", "127.0.0.1", 7890)
bot_proxy = ()

witdhxheight = [
    "512x512",
    "512x768",
]

scale: int = 11
steps: int = 40
default_uc = [
    "extra limbs",
    "lowres",
    "bad anatomy",
    "bad hands",
    "text",
    "error",
    "missing fingers",
    "extra digit",
    "fewer digits",
    "cropped",
    "worst quality",
    "low quality",
    "normal quality",
    "jpeg artifacts",
    "signature",
    "watermark",
    "username",
    "blurry",
]
