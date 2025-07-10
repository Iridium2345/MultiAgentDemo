"""
知识库配置模块
包含知识库相关的配置类
"""

from typing import Any, Optional

class KnowledgeBaseConfig:
    """知识库配置类"""
    __name: str
    __description: str
    __type: str
    __connection_info: dict[str, Any]
    __metadata: dict[str, Any]
    
    def __init__(self, name: str, description: str = "", type: str = "", connection_info: Optional[dict[str, Any]] = None, metadata: Optional[dict[str, Any]] = None, **_kwargs: Any) -> None:
        self.__name = name
        self.__description = description
        self.__type = type
        self.__connection_info = connection_info or {}
        self.__metadata = metadata or {}
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def description(self) -> str:
        return self.__description
    
    @property
    def type(self) -> str:
        return self.__type
    
    @property
    def connection_info(self) -> dict[str, Any]:
        return self.__connection_info.copy()
    
    @property
    def metadata(self) -> dict[str, Any]:
        return self.__metadata.copy()
    
    def __str__(self) -> str:
        return f"{self.__name}: {self.__description} (type={self.__type})" 