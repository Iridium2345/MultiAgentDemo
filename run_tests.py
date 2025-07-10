#!/usr/bin/env python3
"""
测试运行器 - 运行所有聊天代理测试
"""

import sys
import os
from unittest.mock import Mock, patch

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_chat_agent():
    """测试 ChatAgent 类的基本功能"""
    print("🧪 测试 ChatAgent 类...")
    
    try:
        # 测试模块导入
        from multi_agent_framework.chat_agent import ChatAgent
        print("✅ ChatAgent 模块导入成功")
        
        # 测试基本功能（使用模拟）
        with patch('multi_agent_framework.chat_agent.load_agent_config') as mock_load_config, \
             patch('multi_agent_framework.chat_agent.ApiKeys') as mock_api_keys, \
             patch('multi_agent_framework.chat_agent.ChatOpenAI') as mock_chat_openai:
            
            # 设置模拟
            mock_config = Mock()
            mock_config.config = {'system_prompt': 'You are helpful.'}
            mock_load_config.return_value = mock_config
            
            mock_api_keys_instance = Mock()
            mock_key_info = Mock()
            mock_key_info.key = 'test_key'
            mock_api_keys_instance.key_of.return_value = mock_key_info
            mock_api_keys.return_value = mock_api_keys_instance
            
            mock_chat_openai.return_value = Mock()
            
            # 创建并测试 ChatAgent
            agent = ChatAgent('test_config.yaml')
            assert agent.config_path == 'test_config.yaml'
            assert len(agent.chat_history) == 1  # 系统提示
            print("✅ ChatAgent 初始化测试通过")
            
            # 测试重置历史
            agent.chat_history.append(Mock())
            agent.reset_history()
            assert len(agent.chat_history) == 1
            print("✅ ChatAgent 历史重置测试通过")
            
    except Exception as e:
        print(f"❌ ChatAgent 测试失败: {e}")
        return False
    
    return True

def test_simple_chat_agent():
    """测试 SimpleChatAgent 类的基本功能"""
    print("\n🧪 测试 SimpleChatAgent 类...")
    
    try:
        # 测试模块导入
        from multi_agent_framework.simple_chat import SimpleChatAgent
        print("✅ SimpleChatAgent 模块导入成功")
        
        # 测试基本功能（使用模拟）
        with patch('multi_agent_framework.simple_chat.load_agent_config') as mock_load_config, \
             patch('multi_agent_framework.simple_chat.ApiKeys') as mock_api_keys:
            
            # 设置模拟
            mock_config = Mock()
            mock_config.name = 'simple_agent'
            mock_config.config = {'system_prompt': 'You are helpful.'}
            mock_load_config.return_value = mock_config
            mock_api_keys.return_value = Mock()
            
            # 创建并测试 SimpleChatAgent
            agent = SimpleChatAgent('test_config.yaml')
            assert agent.config_path == 'test_config.yaml'
            assert len(agent.chat_history) == 1  # 系统提示
            print("✅ SimpleChatAgent 初始化测试通过")
            
            # 测试对话功能
            response = agent.chat("Hello")
            assert "simple_agent" in response
            assert "Hello" in response
            assert len(agent.chat_history) == 3  # 系统提示 + 用户 + AI
            print("✅ SimpleChatAgent 对话测试通过")
            
            # 测试历史操作
            history = agent.get_history()
            assert len(history) == 3
            assert history is not agent.chat_history  # 确保是副本
            
            agent.reset_history()
            assert len(agent.chat_history) == 1
            print("✅ SimpleChatAgent 历史操作测试通过")
            
    except Exception as e:
        print(f"❌ SimpleChatAgent 测试失败: {e}")
        return False
    
    return True

def test_api_key_handling():
    """测试 API 密钥处理功能"""
    print("\n🧪 测试 API 密钥处理...")
    
    try:
        from multi_agent_framework.simple_chat import SimpleChatAgent
        
        # 测试 OpenAI 密钥
        with patch('multi_agent_framework.simple_chat.load_agent_config') as mock_load_config, \
             patch('multi_agent_framework.simple_chat.ApiKeys') as mock_api_keys:
            
            mock_config = Mock()
            mock_config.config = {
                'model_config': {
                    'provider': 'OpenAI',
                    'model': 'gpt-3.5-turbo'
                }
            }
            mock_load_config.return_value = mock_config
            
            mock_api_keys_instance = Mock()
            mock_key_info = Mock()
            mock_key_info.key = 'test_openai_key'
            mock_api_keys_instance.key_of.return_value = mock_key_info
            mock_api_keys.return_value = mock_api_keys_instance
            
            agent = SimpleChatAgent('test_config.yaml')
            api_key = agent.get_api_key()
            assert api_key == 'test_openai_key'
            print("✅ OpenAI API 密钥测试通过")
        
        # 测试 DeepSeek 密钥
        with patch('multi_agent_framework.simple_chat.load_agent_config') as mock_load_config, \
             patch('multi_agent_framework.simple_chat.ApiKeys') as mock_api_keys:
            
            mock_config = Mock()
            mock_config.config = {
                'model_config': {
                    'provider': 'DeepSeek',
                    'model': 'deepseek-chat'
                }
            }
            mock_load_config.return_value = mock_config
            
            mock_api_keys_instance = Mock()
            mock_key_info = Mock()
            mock_key_info.key = 'test_deepseek_key'
            mock_api_keys_instance.key_of.return_value = mock_key_info
            mock_api_keys.return_value = mock_api_keys_instance
            
            agent = SimpleChatAgent('test_config.yaml')
            api_key = agent.get_api_key()
            assert api_key == 'test_deepseek_key'
            print("✅ DeepSeek API 密钥测试通过")
            
    except Exception as e:
        print(f"❌ API 密钥处理测试失败: {e}")
        return False
    
    return True

def test_error_handling():
    """测试错误处理功能"""
    print("\n🧪 测试错误处理...")
    
    try:
        from multi_agent_framework.simple_chat import SimpleChatAgent
        
        # 测试 API 密钥不存在的情况
        with patch('multi_agent_framework.simple_chat.load_agent_config') as mock_load_config, \
             patch('multi_agent_framework.simple_chat.ApiKeys') as mock_api_keys:
            
            mock_config = Mock()
            mock_config.config = {
                'model_config': {
                    'provider': 'OpenAI',
                    'model': 'gpt-3.5-turbo'
                }
            }
            mock_load_config.return_value = mock_config
            
            mock_api_keys_instance = Mock()
            mock_api_keys_instance.key_of.side_effect = KeyError("API key not found")
            mock_api_keys.return_value = mock_api_keys_instance
            
            agent = SimpleChatAgent('test_config.yaml')
            
            try:
                agent.get_api_key()
                assert False, "应该抛出 ValueError"
            except ValueError as e:
                assert "未找到" in str(e)
                print("✅ API 密钥缺失错误处理测试通过")
            
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False
    
    return True

def main():
    """主函数 - 运行所有测试"""
    print("🚀 开始运行聊天代理测试套件...")
    print("=" * 50)
    
    tests = [
        test_chat_agent,
        test_simple_chat_agent,
        test_api_key_handling,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_func.__name__} 通过")
            else:
                failed += 1
                print(f"❌ {test_func.__name__} 失败")
        except Exception as e:
            failed += 1
            print(f"❌ {test_func.__name__} 异常: {e}")
    
    print("=" * 50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！")
        return True
    else:
        print("💔 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 