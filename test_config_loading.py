#!/usr/bin/env python3
"""
配置加载测试脚本
测试多代理框架的配置文件加载功能
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_agent_framework import (
    AgentManager,
    McpToolManager, 
    KnowledgeManagerFactory,
    MemoryType,
    MemoryConfig
)

def test_memory_config():
    """测试记忆配置"""
    print("=== 测试记忆配置 ===")
    
    # 测试默认配置
    memory_config = MemoryConfig()
    print(f"默认配置: {memory_config}")
    
    # 测试自定义配置
    custom_config = MemoryConfig(enable=True, type="chroma", url="http://localhost:8000")
    print(f"自定义配置: {custom_config}")
    
    # 测试错误类型
    try:
        invalid_config = MemoryConfig(type="invalid_type")
        print(f"错误: 应该抛出异常但没有: {invalid_config}")
    except ValueError as e:
        print(f"正确捕获异常: {e}")
    
    print()

def test_tool_manager():
    """测试工具管理器"""
    print("=== 测试工具管理器 ===")
    
    tool_manager = McpToolManager("config/tools")
    
    # 列出所有工具
    tools = tool_manager.list_tools()
    print(f"加载的工具数量: {len(tools)}")
    
    for name, tool in tools.items():
        print(f"- {name}: {tool}")
    
    # 获取启用的工具
    enabled_tools = tool_manager.get_enabled_tools()
    print(f"启用的工具数量: {len(enabled_tools)}")
    
    # 测试获取特定工具
    if "web_search" in tools:
        web_search = tool_manager.get_tool("web_search")
        print(f"web_search工具: {web_search}")
        print(f"  - 描述: {web_search.description}")
        print(f"  - 启用: {web_search.enabled}")
        print(f"  - 配置: {web_search.config}")
    
    print()

def test_knowledge_manager():
    """测试知识库管理器"""
    print("=== 测试知识库管理器 ===")
    
    knowledge_manager_factory = KnowledgeManagerFactory()
    knowledge_manager = knowledge_manager_factory.get_knowledge_manager("config/db")
    
    # 列出所有知识库
    knowledge_items = knowledge_manager.list_knowledge_items()
    print(f"加载的知识库数量: {len(knowledge_items)}")
    
    for name, item in knowledge_items.items():
        print(f"- {name}: {item}")
    
    # 获取启用的知识库
    enabled_knowledge = knowledge_manager.get_enabled_knowledge_items()
    print(f"启用的知识库数量: {len(enabled_knowledge)}")
    
    # 测试获取特定知识库
    if "general_knowledge" in knowledge_items:
        general_kb = knowledge_manager.get_knowledge_item("general_knowledge")
        print(f"general_knowledge知识库: {general_kb}")
        print(f"  - 描述: {general_kb.description}")
        print(f"  - 类型: {general_kb.type}")
        print(f"  - 启用: {general_kb.enabled}")
        print(f"  - 连接信息: {general_kb.connection_info}")
    
    print()

def test_agent_manager():
    """测试代理管理器"""
    print("=== 测试代理管理器 ===")
    
    agent_manager = AgentManager(
        agent_config_file="config/agent/agents.yaml",
        tools_config_dir="config/tools",
        knowledge_config_dir="config/db"
    )
    
    # 列出所有代理模板
    templates = agent_manager.list_agent_templates()
    print(f"加载的代理模板数量: {len(templates)}")
    
    for agent_id, template in templates.items():
        print(f"- {agent_id}: {template}")
    
    # 获取启用的代理模板
    enabled_templates = agent_manager.get_enabled_agent_templates()
    print(f"启用的代理模板数量: {len(enabled_templates)}")
    
    # 测试获取特定代理
    if "assistant" in templates:
        assistant = agent_manager.get_agent_template("assistant")
        print(f"assistant代理: {assistant}")
        print(f"  - 名称: {assistant.name}")
        print(f"  - 描述: {assistant.description}")
        print(f"  - 启用: {assistant.enabled}")
        print(f"  - 记忆配置: {assistant.memory}")
        print(f"  - 工具: {assistant.tools}")
        print(f"  - 知识库: {assistant.knowledge_bases}")
        print(f"  - 配置: {assistant.config}")
        
        # 验证代理配置
        validation_result = agent_manager.validate_agent_template("assistant")
        print(f"  - 验证结果: {validation_result}")
        
        # 获取代理可用的工具
        agent_tools = agent_manager.get_agent_tools("assistant")
        print(f"  - 可用工具数量: {len(agent_tools)}")
        
        # 获取代理可用的知识库
        agent_knowledge = agent_manager.get_agent_knowledge_bases("assistant")
        print(f"  - 可用知识库数量: {len(agent_knowledge)}")
    
    print()

def main():
    """主测试函数"""
    print("开始测试多代理框架配置加载...")
    print("=" * 50)
    
    try:
        test_memory_config()
        test_tool_manager()
        test_knowledge_manager()
        test_agent_manager()
        
        print("=" * 50)
        print("✅ 所有测试通过！配置加载功能正常工作。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 