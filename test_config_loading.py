#!/usr/bin/env python3
"""
配置类测试脚本
测试多代理框架的配置类功能
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_agent_framework.config import (
    MemoryConfig,
    McpTool,
    KnowledgeItem,
    AgentTemplate
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

def test_mcp_tool():
    """测试MCP工具配置"""
    print("=== 测试MCP工具配置 ===")
    
    # 创建工具配置
    tool = McpTool(
        name="web_search",
        description="网络搜索工具",
        schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索查询"}
            },
            "required": ["query"]
        },
        config={
            "api_key": "${SEARCH_API_KEY}",
            "endpoint": "https://api.search.example.com"
        }
    )
    
    print(f"工具配置: {tool}")
    print(f"  - 名称: {tool.name}")
    print(f"  - 描述: {tool.description}")
    print(f"  - 模式: {tool.schema}")
    print(f"  - 配置: {tool.config}")
    
    print()

def test_knowledge_item():
    """测试知识库配置"""
    print("=== 测试知识库配置 ===")
    
    # 创建知识库配置
    knowledge = KnowledgeItem(
        name="general_knowledge",
        description="通用知识库",
        type="vector_db",
        connection_info={
            "host": "localhost",
            "port": 6333,
            "collection_name": "general_knowledge"
        },
        metadata={
            "last_updated": "2024-01-01",
            "document_count": 10000
        }
    )
    
    print(f"知识库配置: {knowledge}")
    print(f"  - 名称: {knowledge.name}")
    print(f"  - 描述: {knowledge.description}")
    print(f"  - 类型: {knowledge.type}")
    print(f"  - 连接信息: {knowledge.connection_info}")
    print(f"  - 元数据: {knowledge.metadata}")
    
    print()

def test_agent_template():
    """测试代理模板配置"""
    print("=== 测试代理模板配置 ===")
    
    # 创建代理模板配置
    agent = AgentTemplate(
        id="assistant",
        name="Assistant",
        description="通用助手代理",
        memory={
            "type": "chroma",
            "enabled": True,
            "url": "http://localhost:8000"
        },
        tools=["web_search", "url_fetcher"],
        knowledge_bases=["general_knowledge", "faq"],
        config={
            "model": "gpt-3.5-turbo",
            "temperature": 0.7
        }
    )
    
    print(f"代理模板配置: {agent}")
    print(f"  - ID: {agent.id}")
    print(f"  - 名称: {agent.name}")
    print(f"  - 描述: {agent.description}")
    print(f"  - 记忆配置: {agent.memory}")
    print(f"  - 工具: {agent.tools}")
    print(f"  - 知识库: {agent.knowledge_bases}")
    print(f"  - 其他配置: {agent.config}")
    
    print()

def main():
    """主测试函数"""
    print("开始测试多代理框架配置类...")
    print("=" * 50)
    
    try:
        test_memory_config()
        test_mcp_tool()
        test_knowledge_item()
        test_agent_template()
        
        print("=" * 50)
        print("✅ 所有配置类测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 