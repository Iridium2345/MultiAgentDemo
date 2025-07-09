from .mcp_tools import McpToolManager, McpTool
from .memory_manager import MemoryConfig, MemoryType
from .knowledge_manager import KnowledgeManagerFactory, KnowledgeItem
from typing import Any, Optional, Union
import yaml

class AgentTemplate:
    __id: str
    __name: str
    __description: str
    __enabled: bool
    __memory: MemoryConfig
    __tools: list[str]
    __knowledge_bases: list[str]
    __config: dict[str, Any]
    
    def __init__(self, id: str, name: str = "", description: str = "", enabled: bool = True, 
                 memory: Optional[Union[dict[str, Any], MemoryConfig]] = None, 
                 tools: Optional[list[str]] = None, 
                 knowledge_bases: Optional[list[str]] = None,
                 config: Optional[dict[str, Any]] = None,
                 **_kwargs: Any) -> None:
        self.__id = id
        self.__name = name or id
        self.__description = description
        self.__enabled = enabled
        
        # 处理 memory 配置
        if isinstance(memory, dict):
            self.__memory = MemoryConfig(**memory)
        elif memory is None:
            self.__memory = MemoryConfig(enable=False, type=MemoryType.CHROMA.value, url="")
        else:
            self.__memory = memory
            
        self.__tools = tools or []
        self.__knowledge_bases = knowledge_bases or []
        self.__config = config or {}
    
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
    def enabled(self) -> bool:
        return self.__enabled
    
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
        return f"{self.__id}: {self.__name} (enabled={self.__enabled})"


class AgentTemplates:
    __templates: dict[str, AgentTemplate]
    
    def __init__(self, config_file: str = "config/agent/agents.yaml") -> None:
        self.__templates = {}
        self._load_templates(config_file)
    
    def _load_templates(self, config_file: str) -> None:
        """从配置文件加载代理模板"""
        import os
        
        if not os.path.exists(config_file):
            print(f"警告: 代理配置文件 {config_file} 不存在")
            return
        
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                templates_data = yaml.load(f.read(), yaml.FullLoader)
                if templates_data:
                    for agent_id, agent_config in templates_data.items():
                        self.__templates[agent_id] = AgentTemplate(agent_id, **agent_config)
        except Exception as e:
            print(f"警告: 加载代理配置文件 {config_file} 失败: {e}")
    
    def list_templates(self) -> dict[str, AgentTemplate]:
        return self.__templates.copy()
    
    def get_template(self, template_id: str) -> AgentTemplate:
        if template_id not in self.__templates:
            raise KeyError(f"代理模板 {template_id} 未找到")
        return self.__templates[template_id]
    
    def get_enabled_templates(self) -> dict[str, AgentTemplate]:
        return {id: template for id, template in self.__templates.items() if template.enabled}


class AgentManager:
    __agent_templates: AgentTemplates
    __tool_manager: McpToolManager
    __knowledge_manager_factory: KnowledgeManagerFactory
    
    def __init__(self, agent_config_file: str = "config/agent/agents.yaml",
                 tools_config_dir: str = "config/tools",
                 knowledge_config_dir: str = "config/db") -> None:
        # 初始化各个管理器
        self.__agent_templates = AgentTemplates(agent_config_file)
        self.__tool_manager = McpToolManager(tools_config_dir)
        self.__knowledge_manager_factory = KnowledgeManagerFactory()
    
    @property
    def agent_templates(self) -> AgentTemplates:
        return self.__agent_templates
    
    @property
    def tool_manager(self) -> McpToolManager:
        return self.__tool_manager
    
    @property  
    def knowledge_manager_factory(self) -> KnowledgeManagerFactory:
        return self.__knowledge_manager_factory
    
    def get_agent_template(self, agent_id: str) -> AgentTemplate:
        """获取代理模板"""
        return self.__agent_templates.get_template(agent_id)
    
    def list_agent_templates(self) -> dict[str, AgentTemplate]:
        """列出所有代理模板"""
        return self.__agent_templates.list_templates()
    
    def get_enabled_agent_templates(self) -> dict[str, AgentTemplate]:
        """获取已启用的代理模板"""
        return self.__agent_templates.get_enabled_templates()
    
    def validate_agent_template(self, agent_id: str) -> dict[str, list[str]]:
        """验证代理模板配置的有效性"""
        template = self.get_agent_template(agent_id)
        issues: dict[str, list[str]] = {"errors": [], "warnings": []}
        
        # 验证工具
        available_tools = self.__tool_manager.list_tools()
        for tool_name in template.tools:
            if tool_name not in available_tools:
                issues["errors"].append(f"工具 {tool_name} 未找到")
            elif not available_tools[tool_name].enabled:
                issues["warnings"].append(f"工具 {tool_name} 已禁用")
        
        # 验证知识库
        knowledge_manager = self.__knowledge_manager_factory.get_knowledge_manager()
        available_knowledge = knowledge_manager.list_knowledge_items()
        for kb_name in template.knowledge_bases:
            if kb_name not in available_knowledge:
                issues["errors"].append(f"知识库 {kb_name} 未找到")
            elif not available_knowledge[kb_name].enabled:
                issues["warnings"].append(f"知识库 {kb_name} 已禁用")
        
        # 验证记忆配置
        if template.memory.enable:
            if template.memory.type == MemoryType.CHROMA:
                if not template.memory.url:
                    issues["errors"].append("Chroma 记忆库需要提供 URL")
        
        return issues
    
    def get_agent_tools(self, agent_id: str) -> dict[str, McpTool]:
        """获取代理可用的工具"""
        template = self.get_agent_template(agent_id)
        agent_tools: dict[str, McpTool] = {}
        available_tools = self.__tool_manager.list_tools()
        
        for tool_name in template.tools:
            if tool_name in available_tools and available_tools[tool_name].enabled:
                agent_tools[tool_name] = available_tools[tool_name]
        
        return agent_tools
    
    def get_agent_knowledge_bases(self, agent_id: str) -> dict[str, KnowledgeItem]:
        """获取代理可用的知识库"""
        template = self.get_agent_template(agent_id)
        agent_knowledge: dict[str, KnowledgeItem] = {}
        knowledge_manager = self.__knowledge_manager_factory.get_knowledge_manager()
        available_knowledge = knowledge_manager.list_knowledge_items()
        
        for kb_name in template.knowledge_bases:
            if kb_name in available_knowledge and available_knowledge[kb_name].enabled:
                agent_knowledge[kb_name] = available_knowledge[kb_name]
        
        return agent_knowledge
    
    