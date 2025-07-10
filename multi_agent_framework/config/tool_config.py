"""
工具配置的数据模型
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ToolConfig(BaseModel):
    """
    工具的配置模型，使用 Pydantic 进行数据验证。
    """
    description: str = Field(..., description="工具功能的详细描述")
    py_plugin: Optional[str] = Field(None, description="要动态加载的 Python 插件路径，格式为 'module.submodule:function_name'")
    schema_def: Dict[str, Any] = Field(..., alias='schema', description="工具输入参数的 JSON Schema 定义")
    config: Dict[str, Any] = Field({}, description="工具特定的配置，例如 API 密钥、端点等")
    
    class Config:
        populate_by_name = True 