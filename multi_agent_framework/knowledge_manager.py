import yaml
import os
from typing import Any, List, Optional

class KnowledgeItem:
    __name: str
    __description: str
    __type: str
    __connection_info: dict[str, Any]
    __enabled: bool
    __metadata: dict[str, Any]
    
    def __init__(self, name: str, description: str = "", type: str = "", connection_info: Optional[dict[str, Any]] = None, enabled: bool = True, metadata: Optional[dict[str, Any]] = None, **_kwargs: Any) -> None:
        self.__name = name
        self.__description = description
        self.__type = type
        self.__connection_info = connection_info or {}
        self.__enabled = enabled
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
    def enabled(self) -> bool:
        return self.__enabled
    
    @property
    def metadata(self) -> dict[str, Any]:
        return self.__metadata.copy()
    
    def __str__(self) -> str:
        return f"{self.__name}: {self.__description} (type={self.__type}, enabled={self.__enabled})"


class KnowledgeManager:
    __knowledge_items: dict[str, KnowledgeItem]
    
    def __init__(self, config_dir: str = "config/db") -> None:
        self.__knowledge_items = {}
        self._load_knowledge_items(config_dir)
    
    def _load_knowledge_items(self, config_dir: str) -> None:
        """从配置目录加载所有知识库"""
        if not os.path.exists(config_dir):
            print(f"警告: 知识库配置目录 {config_dir} 不存在")
            return
        
        for filename in os.listdir(config_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                knowledge_file = os.path.join(config_dir, filename)
                try:
                    with open(knowledge_file, "r", encoding="utf-8") as f:
                        knowledge_data = yaml.load(f.read(), yaml.FullLoader)
                        if knowledge_data:
                            for kb_name, kb_config in knowledge_data.items():
                                self.__knowledge_items[kb_name] = KnowledgeItem(kb_name, **kb_config)
                except Exception as e:
                    print(f"警告: 加载知识库配置文件 {knowledge_file} 失败: {e}")
    
    def list_knowledge_items(self) -> dict[str, KnowledgeItem]:
        return self.__knowledge_items.copy()
    
    def get_knowledge_item(self, item_name: str) -> KnowledgeItem:
        if item_name not in self.__knowledge_items:
            raise KeyError(f"知识库 {item_name} 未找到")
        return self.__knowledge_items[item_name]
    
    def get_enabled_knowledge_items(self) -> dict[str, KnowledgeItem]:
        return {name: item for name, item in self.__knowledge_items.items() if item.enabled}


class KnowledgeManagerFactory:
    """知识库管理器工厂"""
    _instances: dict[str, KnowledgeManager] = {}
    
    @classmethod
    def get_knowledge_manager(cls, config_dir: str = "config/db") -> KnowledgeManager:
        """获取知识库管理器实例（单例模式）"""
        key = f"{config_dir}"
        if key not in cls._instances:
            cls._instances[key] = KnowledgeManager(config_dir)
        return cls._instances[key]
    
    @classmethod
    def list_knowledge_managers(cls) -> List[str]:
        """列出所有知识库管理器"""
        return list(cls._instances.keys())
    
    @classmethod
    def reload_all(cls) -> None:
        """重新加载所有知识库"""
        cls._instances.clear() 