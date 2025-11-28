from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    allow_groups: list[str] = []
    allow_user: list[str] = [] 
    unzip_password: str | int = None
