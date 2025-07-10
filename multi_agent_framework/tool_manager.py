"""
动态工具加载器和管理器
"""
import logging
import importlib
from typing import Callable, Dict, Any, List
from langchain_core.tools import tool as create_langchain_tool

from .config.loader import load_tool_config
from .config.tool_config import ToolConfig

logger = logging.getLogger(__name__)


def _dynamic_import(plugin_path: str) -> Callable[..., Any]:
    """
    根据路径动态导入一个函数或类。
    
    Args:
        plugin_path: 插件路径，格式为 'module.submodule:function_or_class_name'
        
    Returns:
        可调用的已导入对象。
        
    Raises:
        ImportError: 如果模块或函数无法导入。
    """
    try:
        module_path, object_name = plugin_path.split(":")
        module = importlib.import_module(module_path)
        return getattr(module, object_name)
    except (ValueError, ImportError, AttributeError) as e:
        logger.error(f"动态导入插件 '{plugin_path}' 失败: {e}", exc_info=True)
        raise ImportError(f"无法从 '{plugin_path}' 导入插件。") from e


class ToolManager:
    """
    负责加载、管理和执行工具。
    """
    
    def __init__(self, tool_config_paths: List[str]):
        """
        初始化工具管理器。
        
        Args:
            tool_config_paths: 工具配置文件路径的列表。
        """
        self.tools: Dict[str, ToolConfig] = {}
        self.callables: Dict[str, Callable[..., Any]] = {}
        self._load_tools(tool_config_paths)

    def _load_tools(self, tool_config_paths: List[str]) -> None:
        """加载所有在配置文件中定义的工具。"""
        logger.info(f"正在从 {len(tool_config_paths)} 个路径加载工具...")
        for path in tool_config_paths:
            try:
                config = load_tool_config(path)
                if config.py_plugin:
                    tool_name = config.py_plugin.split(":")[1]
                    self.tools[tool_name] = config
                    self.callables[tool_name] = _dynamic_import(config.py_plugin)
                    logger.info(f"成功加载工具 '{tool_name}' (来自 {config.py_plugin})")
                else:
                    logger.warning(f"工具配置 {path} 中缺少 'py_plugin' 字段，已跳过。")
            except Exception as e:
                logger.error(f"加载工具配置 {path} 失败: {e}", exc_info=True)

    def list_tools(self) -> List[str]:
        """返回所有已加载工具的名称列表。"""
        return list(self.callables.keys())

    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """获取指定工具的 JSON Schema。"""
        if tool_name not in self.tools:
            raise ValueError(f"工具 '{tool_name}' 未找到。")
        return self.tools[tool_name].schema_def

    def get_langchain_tools(self) -> List[Callable]:
        """将所有已加载的工具转换为 LangChain 工具列表。"""
        lc_tools = []
        for name, config in self.tools.items():
            func = self.callables[name]
            # 使用 langchain 的 @tool 装饰器动态创建工具
            # 这会将函数的签名和 docstring 转换为 LangChain 工具
            lc_tool = create_langchain_tool(func)
            # 手动设置工具名称和描述
            lc_tool.name = name
            lc_tool.description = config.description
            lc_tools.append(lc_tool)
        return lc_tools

    def run_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """
        执行一个工具。
        
        Args:
            tool_name: 要执行的工具名称。
            **kwargs: 传递给工具的参数。
            
        Returns:
            工具的执行结果。
        """
        if tool_name not in self.callables:
            raise ValueError(f"工具 '{tool_name}' 不可用或未加载。")
        
        logger.info(f"正在执行工具 '{tool_name}'，参数: {kwargs}")
        tool_callable = self.callables[tool_name]
        
        try:
            result = tool_callable(**kwargs)
            logger.info(f"工具 '{tool_name}' 执行成功。")
            return result
        except Exception as e:
            logger.error(f"执行工具 '{tool_name}' 时出错: {e}", exc_info=True)
            return f"执行工具 '{tool_name}' 失败: {e}" 