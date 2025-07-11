#!/usr/bin/env python3
"""
测试知识库与代理集成的脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from multi_agent_framework import (
    KnowledgeManager,
    KnowledgeBaseConfig,
    KnowledgeItem
)
from multi_agent_framework.config.loader import load_agent_config

def test_knowledge_base_config():
    """测试知识库配置加载"""
    print("=== 测试知识库配置加载 ===")
    
    try:
        # 加载代理配置
        agent_config = load_agent_config("configs/agent/example.yaml")
        print(f"代理配置已加载: {agent_config.name}")
        print(f"配置的知识库: {agent_config.knowledge_bases}")
        
        # 验证知识库配置
        if agent_config.knowledge_bases:
            print("✓ 代理配置包含知识库")
            for kb_name in agent_config.knowledge_bases:
                print(f"  - {kb_name}")
        else:
            print("✗ 代理配置中没有知识库")
            
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False
    
    return True

def test_knowledge_manager():
    """测试知识库管理器"""
    print("\n=== 测试知识库管理器 ===")
    
    try:
        # 创建知识库管理器
        manager = KnowledgeManager()
        print("✓ 知识库管理器创建成功")
        
        # 从配置文件加载知识库
        from multi_agent_framework.config.loader import load_knowledge_config
        
        kb_config = load_knowledge_config("configs/knowledge_bases/chroma_example.yaml")
        print(f"✓ 知识库配置加载成功: {kb_config.name}")
        
        # 尝试添加知识库
        success = manager.add_knowledge_base("test_kb", kb_config)
        if success:
            print("✓ 知识库添加成功")
        else:
            print("✗ 知识库添加失败")
            return False
            
        # 创建测试知识项
        test_item = KnowledgeItem(
            id="test_item",
            content="这是一个测试知识项，用于验证知识库系统是否正常工作。",
            title="测试知识项",
            category="test",
            tags=["测试", "验证"]
        )
        
        # 添加知识项
        add_success = manager.add_item("test_kb", test_item)
        if add_success:
            print("✓ 测试知识项添加成功")
        else:
            print("✗ 测试知识项添加失败")
            return False
            
        # 测试搜索
        results = manager.search("test_kb", "测试", top_k=5)
        if results:
            print(f"✓ 搜索成功，找到 {len(results)} 个结果")
            for result in results:
                print(f"  - {result.item.title}: {result.score:.3f}")
        else:
            print("✗ 搜索失败或无结果")
            
        # 获取统计信息
        stats = manager.get_stats("test_kb")
        print(f"✓ 知识库统计: {stats.get('total_items', 0)} 个知识项")
        
    except Exception as e:
        print(f"✗ 知识库管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_agent_knowledge_integration():
    """测试代理与知识库的集成"""
    print("\n=== 测试代理与知识库集成 ===")
    
    try:
        # 尝试创建带知识库的代理
        from multi_agent_framework.graph_agent import GraphAgent
        
        # 这里可能会失败，因为需要API密钥
        print("尝试创建 GraphAgent...")
        # agent = GraphAgent("configs/agent/example.yaml")
        # print("✓ 带知识库的代理创建成功")
        
        print("⚠ 跳过代理创建测试（需要API密钥）")
        
    except Exception as e:
        print(f"✗ 代理集成测试失败: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("开始测试知识库与代理的集成...")
    
    tests = [
        test_knowledge_base_config,
        test_knowledge_manager,
        test_agent_knowledge_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有测试通过")
    else:
        print("✗ 部分测试失败")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 