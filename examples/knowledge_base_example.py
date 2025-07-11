"""
知识库使用示例
演示如何使用基于 Chroma 的知识库系统
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

def main():
    """主函数，演示知识库的基本使用"""
    print("=== 知识库使用示例 ===")
    
    # 1. 创建知识库管理器
    print("\n1. 创建知识库管理器...")
    knowledge_manager = KnowledgeManager()
    
    # 2. 创建知识库配置
    print("\n2. 创建知识库配置...")
    chroma_config = KnowledgeBaseConfig(
        name="demo_knowledge_base",
        description="演示用的知识库",
        type="chroma",
        enable=True,
        connection_info={
            "collection_name": "demo_collection",
            "persist_directory": "./data/demo_chroma"
        }
    )
    
    # 3. 添加知识库
    print("\n3. 添加知识库...")
    success = knowledge_manager.add_knowledge_base("demo_kb", chroma_config)
    if success:
        print("✓ 知识库添加成功")
    else:
        print("✗ 知识库添加失败")
        return
    
    # 4. 创建知识项
    print("\n4. 创建知识项...")
    knowledge_items = [
        KnowledgeItem(
            id="python_intro",
            content="Python是一种高级编程语言，由Guido van Rossum在1991年首次发布。它的设计哲学强调代码的可读性和简洁性。",
            title="Python介绍",
            category="programming",
            tags=["python", "编程", "入门"]
        ),
        KnowledgeItem(
            id="ai_basics",
            content="人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的智能机器。",
            title="人工智能基础",
            category="ai",
            tags=["ai", "人工智能", "机器学习"]
        ),
        KnowledgeItem(
            id="web_dev",
            content="Web开发是创建网站和网络应用程序的过程。它包括前端开发（用户界面）和后端开发（服务器端逻辑）。",
            title="Web开发概述",
            category="web",
            tags=["web", "开发", "前端", "后端"]
        )
    ]
    
    # 5. 添加知识项到知识库
    print("\n5. 添加知识项到知识库...")
    for item in knowledge_items:
        success = knowledge_manager.add_item("demo_kb", item)
        if success:
            print(f"✓ 知识项 '{item.title}' 添加成功")
        else:
            print(f"✗ 知识项 '{item.title}' 添加失败")
    
    # 6. 搜索知识项
    print("\n6. 搜索知识项...")
    search_queries = ["Python编程", "人工智能", "网站开发"]
    
    for query in search_queries:
        print(f"\n搜索查询: '{query}'")
        results = knowledge_manager.search("demo_kb", query, top_k=3)
        
        if results:
            for result in results:
                print(f"  - {result.item.title} (评分: {result.score:.3f})")
                print(f"    内容: {result.item.content[:100]}...")
        else:
            print("  没有找到相关结果")
    
    # 7. 按分类列出知识项
    print("\n7. 按分类列出知识项...")
    categories = ["programming", "ai", "web"]
    
    for category in categories:
        print(f"\n分类: {category}")
        items = knowledge_manager.list_items("demo_kb", category=category)
        for item in items:
            print(f"  - {item.title}")
    
    # 8. 获取知识库统计信息
    print("\n8. 获取知识库统计信息...")
    stats = knowledge_manager.get_stats("demo_kb")
    print(f"总知识项数: {stats.get('total_items', 0)}")
    print(f"分类数: {len(stats.get('categories', []))}")
    print(f"标签数: {len(stats.get('tags', []))}")
    
    # 9. 获取管理器摘要
    print("\n9. 获取管理器摘要...")
    summary = knowledge_manager.get_summary()
    print(f"知识库总数: {summary['total_knowledge_bases']}")
    
    for kb_name, kb_info in summary['knowledge_bases'].items():
        print(f"知识库 '{kb_name}':")
        print(f"  类型: {kb_info['type']}")
        print(f"  描述: {kb_info['description']}")
        print(f"  启用: {kb_info['enabled']}")
        if 'stats' in kb_info:
            print(f"  知识项数: {kb_info['stats'].get('total_items', 0)}")
    
    # 10. 更新知识项
    print("\n10. 更新知识项...")
    updates = {
        "content": "Python是一种高级编程语言，由Guido van Rossum在1991年首次发布。它的设计哲学强调代码的可读性和简洁性。Python广泛应用于Web开发、数据科学、人工智能等领域。",
        "tags": ["python", "编程", "入门", "数据科学"]
    }
    
    success = knowledge_manager.update_item("demo_kb", "python_intro", updates)
    if success:
        print("✓ 知识项更新成功")
        # 重新获取更新后的知识项
        updated_item = knowledge_manager.get_item("demo_kb", "python_intro")
        if updated_item:
            print(f"更新后的内容: {updated_item.content[:150]}...")
            print(f"更新后的标签: {updated_item.tags}")
    else:
        print("✗ 知识项更新失败")
    
    print("\n=== 示例完成 ===")

if __name__ == "__main__":
    main() 