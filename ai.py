import config
import httpx


async def request_api(
    prompt: str,
    seed: int,
    image_base64: str = None,
    scale: int = config.scale,
    steps: int = config.steps,
    uc: str = ", ".join(config.default_uc),
) -> str:
    """请求 ai 生成图片"""
    try:
        async with httpx.AsyncClient(proxies=config.httpx_proxy, timeout=100) as client:
            if "masterpiece" not in prompt:
                prompt = "masterpiece, " + prompt
            if "best quality" not in prompt:
                prompt = "best quality, " + prompt
            if "highres fix" not in prompt:
                prompt = "highres fix, " + prompt
            data = {
                "prompt": f"{prompt}",
                "seed": seed,
                "n_samples": 1,
                "sampler": "k_euler_ancestral",
                "width": 512,
                "height": 512,
                "scale": scale,
                "steps": steps,
                "uc": uc,
            }
            if image_base64:
                data["image"] = image_base64
            pic = await client.post(
                config.ai_api_url,
                json=data,
            )
            if pic.text.startswith("{"):
                res = pic.json()
                if "output" in res:
                    return res["output"][0]
                if "error" in res:
                    raise Exception(res["error"])
            else:
                return pic.text.split("\n")[2][5:]

    except BaseException as e:
        print("图片下载失败 request_api:" + str(e))
        raise BaseException
