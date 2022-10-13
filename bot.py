import asyncio
import base64
from math import e
import random
import time
from typing import List
import uuid
from telethon import TelegramClient, events, sync, Button
from telethon.tl.types import MessageMediaPhoto
from telegram_command import *
import config
import ai
from io import BytesIO
from PIL import Image


def get_seed():
    return random.randint(0, 2**32)


def get_uuid():
    return str(uuid.uuid4())


bot = TelegramClient(
    "bot",
    config.API_ID,
    config.API_HASH,
    proxy=config.bot_proxy,
).start(bot_token=config.BOT_TOKEN)

CD_TIME = 60
generate_time = {
    #     id:上次生成time
}
MP = {
    "mp": 2,  # mp 实时值
    "mp_max": 2,  # mp 总量
    "last_up_time": time.time(),  # mp上次恢复时间
    "up_speed": 1,  # mp 恢复速度
    "up_time": 20,  # mp 恢复间隔时间 s
}


def get_at(event: events.CallbackQuery.Event):
    if event.sender.username:
        return f" \n@{event.sender.username}"
    else:
        # 文字提及用户
        return f" [@{event.sender.first_name}](tg://user?id={event.sender_id})"


async def check_cd(event: events.CallbackQuery.Event):
    global generate_time
    global MP
    # 全局 CD
    if MP["mp"] > MP["mp_max"]:
        MP["mp"] = MP["mp_max"]
    if MP["mp"] < MP["mp_max"]:
        if (time.time() - MP["last_up_time"]) >= MP["up_time"]:
            MP["mp"] += round(
                MP["up_speed"] * ((time.time() - MP["last_up_time"]) / MP["up_time"])
            )
            MP["last_up_time"] = time.time()
        if MP["mp"] <= 0:
            await event.reply(f"MP 不足, 请稍后再试！{get_at(event=event)}")
            return False
    # 个人技能 cd
    if last_time := generate_time.get(event.sender_id):
        if time.time() - last_time <= float(CD_TIME):
            await event.reply(
                f"您的生成技能CD中，请 {round(last_time + CD_TIME - time.time())}s 后再试！{get_at(event=event)}"
            )
            return False
    generate_time.update({event.sender_id: time.time()})
    MP["mp"] -= 1
    return True


class AICommands:
    text2image = CommandInfo(
        name="text2image", command="text2image", description="文字生成图片"
    )
    image2image = CommandInfo(
        name="image2image", command="image2image", description="图片生成图片"
    )


@bot.on(events.NewMessage(pattern="/start"))
async def start(event: events.newmessage.NewMessage.Event):
    btns = []
    for command in AICommands.__dict__.values():
        if isinstance(command, CommandInfo):
            btn = Button.inline(command.name, data=command.command)
            btns.append(btn)
    # 一行显示 3 个按钮
    btns = [btns[i : i + 3] for i in range(0, len(btns), 3)]
    await event.reply(
        "选择操作:",
        buttons=btns,
    )


async def draw_image(event: events.CallbackQuery.Event, image_base64: str = None):
    uuid_prefix = get_uuid()
    msg_event = await wait_msg_callback(
        bot=bot, event=event, msg="输入 prompt", remove_text=True
    )
    prompt = str(msg_event.message)
    data = {
        "prompt": f"{prompt}",
        "seed": get_seed(),
        "uc": ", ".join(config.default_uc),
        "scale": 11,
        "steps": 40,
        "size": "512x512",
    }

    btns = [
        InputButton(text="prompt", data=f"{uuid_prefix}#prompt"),
        InputButton(text="uc", data=f"{uuid_prefix}#uc"),
        InputButton(text="scale", data=f"{uuid_prefix}#scale"),
        InputButton(text="steps", data=f"{uuid_prefix}#steps"),
        InputButton(text="seed", data=f"{uuid_prefix}#seed"),
        InputButton(text="size", data=f"{uuid_prefix}#size"),
        InputButton(text="直接生成", data=f"{uuid_prefix}#generate"),
    ]
    while True:
        text_tips = (
            f"scale: {data['scale']}\nsteps: {data['steps']}\nsize: {data['size']}\nseed: {data['seed']}"
        )
        select = await wait_btn_callback(
            bot=bot, event=event, tips_text=f"{text_tips}\n设置其他参数:", btns=btns
        )

        if select.endswith("#generate"):
            break
        elif select.endswith("#size"):
            wh = await wait_btn_callback(
                bot=bot,
                event=event,
                tips_text=f"设置 size",
                btns=[
                    InputButton(text=x, data=f"{uuid_prefix}#size#{x}")
                    for x in config.witdhxheight
                ],
            )
            data["size"] = wh.split("#")[-1]
        else:
            key = select.split("#")[1]
            value = str(
                (
                    await wait_msg_callback(
                        bot=bot,
                        event=event,
                        msg=f"当前值:\n{data[key]}\n设置 {key}",
                        remove_text=True,
                    )
                ).message
            )
            data[key] = value
    if image_base64:
        data["image_base64"] = image_base64
    try:
        msg = await msg_event.reply("图片生成中...")
        start = time.time()
        res_image_base64 = await ai.request_api(
            **data,
        )
        end = time.time()
        await msg.delete()
        await msg_event.reply(
            f"Steps: {config.steps}, Sampler: Euler a, CFG scale: {config.scale}, Size: {data['size']}, Seed: {data['seed']}\n耗时：{round(end - start, 3)}s",
            file=base64.b64decode(res_image_base64),
        )

    except Exception as e:
        await msg_event.reply(f"图片生成失败 {e}")


# 将图片转化为 base64
async def get_pic_base64(content, file_type) -> str:
    im = Image.open(content)
    jpeg_image_buffer = BytesIO()
    im.save(jpeg_image_buffer, file_type)
    res = str(base64.b64encode(jpeg_image_buffer.getvalue()), encoding="utf-8")
    return res


@bot.on(events.CallbackQuery(data=AICommands.text2image.command))  # type: ignore
async def text2image(event: events.CallbackQuery.Event) -> None:
    # await event.delete()
    if not await check_cd(event):
        return
    await draw_image(event=event)


@bot.on(events.CallbackQuery(data=AICommands.image2image.command))  # type: ignore
async def image2image(event: events.CallbackQuery.Event) -> None:
    # await event.delete()
    if not await check_cd(event):
        return
    # 等待用户上传图片
    msg = await wait_msg_callback(bot=bot, event=event, msg="上传图片", remove_text=True)
    photo: MessageMediaPhoto = msg.media
    if not photo:
        await msg.reply("你的图片呢？")
        return

    image = await bot.download_media(
        photo, file=f"images/{event.sender_id}-{get_uuid()}.jpg"
    )
    image_base64 = await get_pic_base64(image, "jpeg")
    await draw_image(event=event, image_base64=image_base64)


@bot.on(events.NewMessage(pattern="/ai"))
async def fast_start(event: events.newmessage.NewMessage.Event):
    if not await check_cd(event):
        return
    msg_event = await wait_msg_callback(
        bot=bot, event=event, msg="输入 prompt:", remove_text=True
    )
    prompt = str(msg_event.message)
    try:
        seed = get_seed()
        msg = await event.reply("图片生成中...")
        start = time.time()
        image_base64 = await ai.request_api(prompt=prompt, seed=seed)
        end = time.time()
        await msg.delete()
        await msg_event.reply(
            f"Steps: {config.steps}, Sampler: Euler a, CFG scale: {config.scale}, Seed: {seed}\n耗时：{round(end - start, 3)}s",
            file=base64.b64decode(image_base64),
        )

    except Exception as e:
        await msg_event.reply(f"图片生成失败 {e}")


with bot:
    bot.loop.run_forever()
