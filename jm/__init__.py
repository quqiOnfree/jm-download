from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, PrivateMessageEvent, Bot
from nonebot.params import CommandArg
import asyncio

import random
import os
from jmcomic import *

from .config import Config
from .jm_download import compress

__plugin_meta__ = PluginMetadata(
    name="JM漫画助手",
    description="一键生成JM漫画链接",
    usage="/jm [漫画ID]",
    extra={
        "example": "/jm 10000",
        "author": "QQOF",
        "version": "1.0.0"
    }
)

config = get_plugin_config(Config)
allow_groups = config.allow_groups

async def async_compress(jm_id: int, password: str):
    """异步压缩漫画"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, compress, jm_id, password)

jm_cmd = on_command("jm", aliases={"JM", "禁漫", "漫画"}, priority=10)
@jm_cmd.handle()
async def handle_jm_command(bot: Bot, event: GroupMessageEvent | PrivateMessageEvent, args: Message = CommandArg()):
    # 群聊检查
    if isinstance(event, GroupMessageEvent):
        # if event.sender.role != "admin" and event.sender.role != "owner" and event.group_id not in ALLOW_GROUPS:
        #     await jm_cmd.finish("你所在的群不允许使用此功能")
        if str(event.group_id) not in allow_groups:
            await jm_cmd.finish("你所在的群不允许使用此功能：{}".format(event.group_id))

    # 获取用户输入的漫画ID
    comic_id = args.extract_plain_text().strip()
    
    # 验证输入
    if not comic_id:
        await jm_cmd.finish("请输入漫画ID，例如：/jm 10000")
    
    if not comic_id.isdigit():
        await jm_cmd.finish("漫画ID必须是数字，例如：/jm 10000")

    message_result = await jm_cmd.send(f"正在下载漫画 {comic_id}，请稍候...")
    
    password = str(random.randint(100000, 999999999999))
    try:
        file = await async_compress(int(comic_id), password)
        await bot.delete_msg(message_id=message_result["message_id"])
        file_cq = "[CQ:file,file=file://{}]".format(file)
        await jm_cmd.send(message=Message(file_cq))
        os.remove(file)
    except PartialDownloadFailedException:
        await jm_cmd.finish(f'下载出现部分失败')
    except Exception as e:
        await jm_cmd.finish("出现错误：", e)
    