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
from .rule import check_allow_group, check_allow_user
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
unzip_password = config.unzip_password

async def async_compress(jm_id: int, password: str | int):
    """异步压缩漫画"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, compress, jm_id, password)

jm_cmd = on_command("jm", aliases={"JM", "禁漫", "漫画"}, priority=10)

@jm_cmd.handle()
async def handle_jm_command(bot: Bot, event: GroupMessageEvent | PrivateMessageEvent, args: Message = CommandArg()):
    group_id = event.group_id
    user_id = event.user_id
    # 检查权限
    if isinstance(event, GroupMessageEvent) and not check_allow_group(str(group_id)):
        return
    if isinstance(event, PrivateMessageEvent) and not check_allow_user(str(user_id)):
        return
        
    # 获取用户输入的漫画ID
    comic_id = args.extract_plain_text().strip()
    
    # 验证输入
    if not comic_id:
        await jm_cmd.finish("请输入漫画ID，例如：/jm 10000\n返回的文件格式：jmid\"漫画ID\"pwd\"密码\".zip\n密码是随机生成的，解压时需要输入")
    
    if not comic_id.isdigit():
        await jm_cmd.finish("漫画ID必须是数字，例如：/jm 10000")

    message_result = await jm_cmd.send(f"正在下载漫画{comic_id}，请稍候...")
    message_id = message_result["message_id"]
    
    if unzip_password:
        password = str(unzip_password)
    else:
        password = str(random.randint(1<<62, 1<<63))

    try:
        file = await async_compress(int(comic_id), password)
        await jm_cmd.send(f'漫画:{comic_id}下载完成，正在发送\n解压密码：{password}')
        await bot.delete_msg(message_id=message_id)

        file_cq = "[CQ:file,file=file://{}]".format(file)
        await jm_cmd.send(message=Message(file_cq))
        os.remove(file)

    except PartialDownloadFailedException:
        await bot.delete_msg(message_id=message_id)
        await jm_cmd.finish(f'漫画:{comic_id}下载出现部分失败')

    except Exception as e:
        await bot.delete_msg(message_id=message_id)
        await jm_cmd.finish(f"出现错误：{e}")
    