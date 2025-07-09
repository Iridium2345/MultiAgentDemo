from typing import Any
from enum import Enum

class MemoryType(Enum):
    """记忆库类型枚举"""
    CHROMA = "chroma"
    
    @classmethod
    def from_string(cls, value: str) -> "MemoryType":
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"不支持的记忆库类型: {value}，支持的类型: {[t.value for t in cls]}")

class MemoryConfig:
    """记忆库配置"""
    __enable: bool
    __type: MemoryType
    __url: str
    
    def __init__(self, enable: bool = True, type: str = "chroma", url: str = "http://localhost:8000", **_kwargs: Any) -> None:
        self.__enable = enable
        self.__type = MemoryType.from_string(type)
        self.__url = url
    
    @property
    def enable(self) -> bool:
        return self.__enable
    
    @property
    def type(self) -> MemoryType:
        return self.__type
    
    @property
    def url(self) -> str:
        return self.__url
    
    def __str__(self) -> str:
        return f"MemoryConfig(enable={self.__enable}, type={self.__type.value}, url={self.__url})"

 