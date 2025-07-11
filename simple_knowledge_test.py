#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    print("=== 测试导入 ===")
    try:
        from multi_agent_framework.knowledge_base import KnowledgeItem
        from multi_agent_framework.knowledge_manager import KnowledgeManager
        from multi_agent_framework.config.knowledge_config import KnowledgeBaseConfig
        print("✓ 核心模块导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_basic():
    print("\n=== 测试基本功能 ===")
    try:
        from multi_agent_framework.knowledge_base import KnowledgeItem
        from multi_agent_framework.config.knowledge_config import KnowledgeBaseConfig
        
        item = KnowledgeItem(id="test", content="测试内容", title="测试")
        config = KnowledgeBaseConfig(name="test_kb", type="chroma")
        
        print(f"✓ 知识项: {item.title}")
        print(f"✓ 配置: {config.name}")
        return True
    except Exception as e:
        print(f"✗ 基本功能失败: {e}")
        return False

def main():
    print("知识库核心功能测试")
    tests = [test_imports, test_basic]
    passed = sum(1 for test in tests if test())
    print(f"\n结果: {passed}/{len(tests)} 通过")
    return passed == len(tests)

if __name__ == "__main__":
    main() 