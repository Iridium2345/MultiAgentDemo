"""
Multi-Agent Framework
"""
from .config import (
    AgentConfig,
    KnowledgeBaseConfig,
    MemoryConfig,
    MemoryType,
    ToolConfig
)

# 知识库相关组件 - 不依赖外部库
from .knowledge_base import (
    KnowledgeBase,
    KnowledgeItem,
    KnowledgeType,
    SearchResult
)
from .knowledge_manager import KnowledgeManager

# 可选组件 - 可能依赖外部库
__all__ = [
    "AgentConfig",
    "KnowledgeBaseConfig", 
    "MemoryConfig",
    "MemoryType",
    "ToolConfig",
    "KnowledgeBase",
    "KnowledgeItem",
    "KnowledgeType",
    "SearchResult",
    "KnowledgeManager",
]

# 尝试导入可选组件
try:
    from .tool_manager import ToolManager
    __all__.append("ToolManager")
except ImportError:
    pass

try:
    from .graph_agent import GraphAgent
    __all__.append("GraphAgent")
except ImportError:
    pass

try:
    from .knowledge_bases import ChromaKnowledgeBase
    __all__.append("ChromaKnowledgeBase")
except ImportError:
    pass
