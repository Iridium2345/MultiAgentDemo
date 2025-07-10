"""
代理配置模块
包含代理相关的配置类
"""

from typing import Any, Optional, Union
from .memory_config import MemoryConfig, MemoryType

class AgentConfig:
    """代理模板配置类"""
    __id: str
    __name: str
    __description: str
    __memory: MemoryConfig
    __tools: list[str]
    __knowledge_bases: list[str]
    __config: dict[str, Any]
    
    def __init__(self, id: str, name: str = "", description: str = "", 
                 memory: Optional[Union[dict[str, Any], MemoryConfig]] = None, 
                 tools: Optional[list[str]] = None, 
                 knowledge_bases: Optional[list[str]] = None,
                 config: Optional[dict[str, Any]] = None,
                 **kwargs: Any) -> None:
        self.__id = id
        self.__name = name or id
        self.__description = description
        
        # 处理 memory 配置
        if isinstance(memory, dict):
            self.__memory = MemoryConfig(**memory)
        elif memory is None:
            self.__memory = MemoryConfig(enable=False, type=MemoryType.CHROMA.value, url="")
        else:
            self.__memory = memory
            
        self.__tools = tools or []
        self.__knowledge_bases = knowledge_bases or []
        
        # 将所有额外的配置字段合并到 config 中
        self.__config = config or {}
        self.__config.update(kwargs)
    
    @property
    def id(self) -> str:
        return self.__id
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def description(self) -> str:
        return self.__description
    
    @property
    def memory(self) -> MemoryConfig:
        return self.__memory
    
    @property
    def tools(self) -> list[str]:
        return self.__tools.copy()
    
    @property
    def knowledge_bases(self) -> list[str]:
        return self.__knowledge_bases.copy()
    
    @property
    def config(self) -> dict[str, Any]:
        return self.__config.copy()
    
    def __str__(self) -> str:
        return f"{self.__id}: {self.__name}" 