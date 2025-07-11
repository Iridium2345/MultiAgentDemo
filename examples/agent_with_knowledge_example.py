#!/usr/bin/env python3
"""
带知识库的代理使用示例
演示如何创建和使用集成了知识库的代理
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_agent_framework import (
    KnowledgeManager,
    KnowledgeBaseConfig,
    KnowledgeItem
)
from multi_agent_framework.config.loader import load_agent_config

def setup_knowledge_base():
    """设置知识库并添加示例数据"""
    print("=== 设置知识库 ===")
    
    # 创建知识库管理器
    manager = KnowledgeManager()
    
    # 从配置文件加载知识库
    try:
        from multi_agent_framework.config.loader import load_knowledge_config
        kb_config = load_knowledge_config("configs/knowledge_bases/chroma_example.yaml")
        print(f"✓ 知识库配置加载成功: {kb_config.name}")
        
        # 添加知识库
        success = manager.add_knowledge_base("chroma_example", kb_config)
        if success:
            print("✓ 知识库添加成功")
        else:
            print("✗ 知识库添加失败")
            return None
            
    except Exception as e:
        print(f"✗ 知识库设置失败: {e}")
        return None
    
    # 添加示例知识项
    sample_knowledge = [
        KnowledgeItem(
            id="python_basics",
            content="Python是一种高级编程语言，具有简洁的语法和强大的功能。它广泛应用于Web开发、数据分析、人工智能等领域。Python的特点包括：易于学习、跨平台、丰富的库生态系统。",
            title="Python基础知识",
            category="programming",
            tags=["python", "编程", "基础"]
        ),
        KnowledgeItem(
            id="ai_introduction",
            content="人工智能(AI)是计算机科学的一个分支，目标是创造能够模拟人类智能的机器。AI的主要分支包括机器学习、深度学习、自然语言处理、计算机视觉等。现代AI系统能够处理复杂的任务，如图像识别、语音理解、自动驾驶等。",
            title="人工智能简介",
            category="ai",
            tags=["ai", "人工智能", "机器学习"]
        ),
        KnowledgeItem(
            id="web_development",
            content="Web开发是创建网站和Web应用程序的过程。它通常分为前端开发（用户界面）和后端开发（服务器端逻辑）。前端技术包括HTML、CSS、JavaScript，后端技术包括Python、Java、Node.js等。现代Web开发还涉及数据库、API设计、云部署等。",
            title="Web开发概述",
            category="web",
            tags=["web", "前端", "后端", "开发"]
        ),
        KnowledgeItem(
            id="data_science",
            content="数据科学是一个跨学科领域，结合了统计学、计算机科学和领域专业知识来从数据中提取洞察。数据科学家使用Python、R等工具进行数据清洗、分析、可视化和建模。常用的库包括pandas、numpy、scikit-learn、matplotlib等。",
            title="数据科学入门",
            category="data",
            tags=["数据科学", "分析", "python", "统计"]
        )
    ]
    
    print("\n添加示例知识项...")
    for item in sample_knowledge:
        success = manager.add_item("chroma_example", item)
        if success:
            print(f"✓ 添加知识项: {item.title}")
        else:
            print(f"✗ 添加知识项失败: {item.title}")
    
    return manager

def test_knowledge_search(manager):
    """测试知识库搜索功能"""
    print("\n=== 测试知识库搜索 ===")
    
    test_queries = [
        "Python编程",
        "人工智能",
        "网站开发",
        "数据分析",
        "机器学习算法"
    ]
    
    for query in test_queries:
        print(f"\n搜索查询: '{query}'")
        results = manager.search("chroma_example", query, top_k=3)
        
        if results:
            print(f"找到 {len(results)} 个相关结果:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.item.title} (相关度: {result.score:.3f})")
                print(f"     {result.item.content[:100]}...")
        else:
            print("  没有找到相关结果")

def test_category_and_tag_filtering(manager):
    """测试分类和标签过滤"""
    print("\n=== 测试分类和标签过滤 ===")
    
    # 按分类列出
    categories = ["programming", "ai", "web", "data"]
    for category in categories:
        print(f"\n分类 '{category}' 的知识项:")
        items = manager.list_items("chroma_example", category=category)
        for item in items:
            print(f"  - {item.title}")
    
    # 按标签搜索
    tags = ["python", "ai", "开发"]
    for tag in tags:
        print(f"\n标签 '{tag}' 的知识项:")
        items = manager.list_items("chroma_example", tags=[tag])
        for item in items:
            print(f"  - {item.title}")

def simulate_agent_with_knowledge():
    """模拟带知识库的代理交互"""
    print("\n=== 模拟代理与知识库交互 ===")
    
    # 加载代理配置
    try:
        agent_config = load_agent_config("configs/agent/example.yaml")
        print(f"代理配置: {agent_config.name}")
        print(f"配置的知识库: {agent_config.knowledge_bases}")
        
        # 模拟代理处理用户查询的过程
        user_queries = [
            "我想学习Python编程，有什么建议吗？",
            "人工智能是什么？",
            "如何开始Web开发？",
            "数据科学需要什么技能？"
        ]
        
        print("\n模拟代理响应（基于知识库）:")
        for query in user_queries:
            print(f"\n用户: {query}")
            print("代理: 让我在知识库中搜索相关信息...")
            
            # 这里模拟代理从知识库获取信息的过程
            # 实际的代理会使用 GraphAgent 中的 _knowledge_search_node
            
            # 简化的搜索逻辑
            manager = setup_knowledge_base()
            if manager:
                results = manager.search_all(query, top_k=2)
                
                if results and any(r for r in results.values() if r):
                    print("代理: 基于知识库的信息，我可以告诉您:")
                    for kb_name, kb_results in results.items():
                        for result in kb_results:
                            print(f"  - {result.item.title}: {result.item.content[:150]}...")
                else:
                    print("代理: 抱歉，我在知识库中没有找到相关信息。")
            
    except Exception as e:
        print(f"✗ 代理配置加载失败: {e}")

def main():
    """主函数"""
    print("=== 带知识库的代理使用示例 ===")
    
    # 设置知识库
    manager = setup_knowledge_base()
    if not manager:
        print("✗ 知识库设置失败，退出")
        return
    
    # 测试知识库搜索
    test_knowledge_search(manager)
    
    # 测试分类和标签过滤
    test_category_and_tag_filtering(manager)
    
    # 模拟代理交互
    simulate_agent_with_knowledge()
    
    print("\n=== 示例完成 ===")
    print("提示：要使用完整的代理功能，请配置API密钥并运行GraphAgent")

if __name__ == "__main__":
    main() 