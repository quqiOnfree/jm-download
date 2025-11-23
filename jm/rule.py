from nonebot import get_plugin_config

from .config import Config

config = get_plugin_config(Config)
allow_group = config.allow_groups
allow_user = config.allow_user

def check_allow_group(group_id) -> bool:
    """检查是否允许的群聊"""
    return group_id in allow_group

def check_allow_user(user_id) -> bool:
    """检查是否允许的用户"""
    return user_id in allow_user