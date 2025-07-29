from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    allow_groups: set[str]
