from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, PrivateMessageEvent
from nonebot.params import CommandArg
from nonebot.permission import Permission

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

jm_cmd = on_command("jm", aliases={"JM", "禁漫", "漫画"}, priority=10)
@jm_cmd.handle()
async def handle_jm_command(event: GroupMessageEvent | PrivateMessageEvent, args: Message = CommandArg()):
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
    
    password = str(random.randint(100000, 999999999999))
    try:
        file = compress(int(comic_id), password)
        file_cq = "[CQ:file,file=file://{}]".format(file)
        try:
            await jm_cmd.finish(message=Message(file_cq))
        except Exception:
            pass
        os.remove(file)
    except PartialDownloadFailedException:
        await jm_cmd.finish(f'下载出现部分失败')
    except Exception as e:
        await jm_cmd.finish("出现错误：", e)
    