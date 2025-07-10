"""
配置加载模块
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any

from .agent_config import AgentConfig
from .knowledge_config import KnowledgeBaseConfig
from .tool_config import ToolConfig
from .memory_config import MemoryConfig

# 初始化日志记录器
logger = logging.getLogger(__name__)

# 全局缓存
_agent_config_cache: Dict[str, AgentConfig] = {}
_knowledge_config_cache: Dict[str, KnowledgeBaseConfig] = {}
_memory_config_cache: Dict[str, MemoryConfig] = {}
_tool_config_cache: Dict[str, ToolConfig] = {}


def load_config(file_path: str) -> Dict[str, Any]:
    """从 YAML 文件加载原始配置数据。"""
    logger.debug(f"正在从 {file_path} 加载原始配置...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            logger.debug(f"成功从 {file_path} 加载配置。")
            return config
    except FileNotFoundError:
        logger.error(f"配置文件未找到: {file_path}")
        raise
    except Exception as e:
        logger.error(f"加载或解析配置文件 {file_path} 时出错: {e}", exc_info=True)
        raise


def load_agent_config(file_path: str) -> AgentConfig:
    """加载并验证代理配置。"""
    if file_path in _agent_config_cache:
        logger.debug(f"从缓存返回代理配置: {file_path}")
        return _agent_config_cache[file_path]

    logger.info(f"正在加载代理配置: {file_path}")
    config_data = load_config(file_path)
    
    # 从文件名中提取 id
    config_id = Path(file_path).stem
    config_data['id'] = config_id
    
    # 保留工具和知识库名称作为字符串，不在这里加载配置对象
    # 实际的配置对象将在需要时由相应的管理器加载
    
    # 创建并缓存配置对象
    agent_config = AgentConfig(**config_data)
    
    _agent_config_cache[file_path] = agent_config
    logger.info(f"代理配置 '{agent_config.name}' 已加载并缓存。")
    return agent_config


def load_knowledge_config(file_path: str) -> KnowledgeBaseConfig:
    """加载并验证知识库配置。"""
    if file_path in _knowledge_config_cache:
        logger.debug(f"从缓存返回知识库配置: {file_path}")
        return _knowledge_config_cache[file_path]

    logger.info(f"正在加载知识库配置: {file_path}")
    config_data = load_config(file_path)
    kb_config = KnowledgeBaseConfig(**config_data)
    
    _knowledge_config_cache[file_path] = kb_config
    logger.info(f"知识库配置 '{kb_config.name}' 已加载并缓存。")
    return kb_config


def load_tool_config(file_path: str) -> ToolConfig:
    """加载并验证工具配置。"""
    if file_path in _tool_config_cache:
        logger.debug(f"从缓存返回工具配置: {file_path}")
        return _tool_config_cache[file_path]

    logger.info(f"正在加载工具配置: {file_path}")
    config_data = load_config(file_path)
    tool_config = ToolConfig(**config_data)
    
    _tool_config_cache[file_path] = tool_config
    logger.info(f"工具配置 '{tool_config.description}' 已加载并缓存。")
    return tool_config
    
    
def load_memory_config(file_path:str) -> MemoryConfig:
    """加载并验证内存配置。"""
    if file_path in _memory_config_cache:
        logger.debug(f"从缓存返回内存配置: {file_path}")
        return _memory_config_cache[file_path]
        
    logger.info(f"正在加载内存配置: {file_path}")
    config_data = load_config(file_path)
    memory_config = MemoryConfig(**config_data)
    
    _memory_config_cache[file_path] = memory_config
    logger.info(f"内存配置 '{memory_config.type}' 已加载并缓存。")
    return memory_config 