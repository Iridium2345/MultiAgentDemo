import yaml
from typing import Any, Optional

class McpTool:
    __name: str
    __description: str
    __schema: dict[str, Any]
    __enabled: bool
    __config: dict[str, Any]
    
    def __init__(self, name: str, description: str = "", schema: Optional[dict[str, Any]] = None, enabled: bool = True, config: Optional[dict[str, Any]] = None, **_kwargs: Any) -> None:
        self.__name = name
        self.__description = description
        self.__schema = schema or {}
        self.__enabled = enabled
        self.__config = config or {}
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def description(self) -> str:
        return self.__description
    
    @property
    def schema(self) -> dict[str, Any]:
        return self.__schema.copy()
    
    @property
    def enabled(self) -> bool:
        return self.__enabled
    
    @property
    def config(self) -> dict[str, Any]:
        return self.__config.copy()
    
    def __str__(self) -> str:
        return f"{self.__name}: {self.__description} (enabled={self.__enabled})"


class McpToolManager:
    __tools: dict[str, McpTool]
    
    def __init__(self, config_dir: str = "config/tools") -> None:
        self.__tools = {}
        self._load_tools(config_dir)
    
    def _load_tools(self, config_dir: str) -> None:
        """从配置目录加载所有工具"""
        import os
        
        if not os.path.exists(config_dir):
            print(f"警告: 工具配置目录 {config_dir} 不存在")
            return
        
        for filename in os.listdir(config_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                tool_file = os.path.join(config_dir, filename)
                try:
                    with open(tool_file, "r", encoding="utf-8") as f:
                        tool_data = yaml.load(f.read(), yaml.FullLoader)
                        if tool_data:
                            for tool_name, tool_config in tool_data.items():
                                self.__tools[tool_name] = McpTool(tool_name, **tool_config)
                except Exception as e:
                    print(f"警告: 加载工具配置文件 {tool_file} 失败: {e}")
    
    def list_tools(self) -> dict[str, McpTool]:
        return self.__tools.copy()
    
    def get_tool(self, tool_name: str) -> McpTool:
        if tool_name not in self.__tools:
            raise KeyError(f"MCP 工具 {tool_name} 未找到")
        return self.__tools[tool_name]
    
    def get_enabled_tools(self) -> dict[str, McpTool]:
        return {name: tool for name, tool in self.__tools.items() if tool.enabled}