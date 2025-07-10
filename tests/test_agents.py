"""
测试聊天代理模块
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch

from multi_agent_framework.chat_agent import ChatAgent, InteractiveChatAgent
from multi_agent_framework.simple_chat import SimpleChatAgent


class TestChatAgent(unittest.TestCase):
    """测试 ChatAgent 类"""
    
    def setUp(self):
        """设置测试环境"""
        self.config_data = {
            'name': 'test_agent',
            'description': 'Test agent',
            'config': {
                'model_config': {
                    'provider': 'OpenAI',
                    'model': 'gpt-3.5-turbo',
                    'temperature': 0.7,
                    'max_tokens': 1000
                },
                'system_prompt': 'You are a helpful assistant.'
            },
            'tools': [],
            'knowledge_bases': []
        }
    
    @patch('multi_agent_framework.chat_agent.load_agent_config')
    @patch('multi_agent_framework.chat_agent.ApiKeys')
    @patch('multi_agent_framework.chat_agent.ChatOpenAI')
    def test_init_success(self, mock_chat_openai, mock_api_keys, mock_load_config):
        """测试成功初始化"""
        # 设置模拟
        mock_config = Mock()
        mock_config.name = 'test_agent'
        mock_config.description = 'Test agent'
        mock_config.config = {
            'model_config': {
                'provider': 'OpenAI',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'max_tokens': 1000
            },
            'system_prompt': 'You are a helpful assistant.'
        }
        mock_config.tools = []
        mock_config.knowledge_bases = []
        
        mock_load_config.return_value = mock_config
        
        mock_api_keys_instance = Mock()
        mock_key_info = Mock()
        mock_key_info.key = 'test_api_key'
        mock_api_keys_instance.key_of.return_value = mock_key_info
        mock_api_keys.return_value = mock_api_keys_instance
        
        # 创建 ChatAgent 实例
        agent = ChatAgent('test_config.yaml', 'test_api_keys.yaml')
        
        # 验证
        self.assertEqual(agent.config_path, 'test_config.yaml')
        self.assertEqual(agent.api_keys_path, 'test_api_keys.yaml')
        self.assertEqual(agent.config, mock_config)
        self.assertEqual(len(agent.chat_history), 1)  # 系统提示
        
        mock_load_config.assert_called_once_with('test_config.yaml')
        mock_api_keys.assert_called_once_with('test_api_keys.yaml')
        mock_chat_openai.assert_called_once()
    
    @patch('multi_agent_framework.chat_agent.load_agent_config')
    @patch('multi_agent_framework.chat_agent.ApiKeys')
    def test_init_missing_api_key(self, mock_api_keys, mock_load_config):
        """测试缺少 API 密钥的情况"""
        # 设置模拟
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
        
        # 验证异常
        with self.assertRaises(ValueError):
            ChatAgent('test_config.yaml', 'test_api_keys.yaml')
    
    @patch('multi_agent_framework.chat_agent.load_agent_config')
    @patch('multi_agent_framework.chat_agent.ApiKeys')
    @patch('multi_agent_framework.chat_agent.ChatOpenAI')
    def test_chat_success(self, mock_chat_openai, mock_api_keys, mock_load_config):
        """测试成功对话"""
        # 设置模拟
        mock_config = Mock()
        mock_config.config = {'system_prompt': 'You are helpful.'}
        mock_load_config.return_value = mock_config
        
        mock_api_keys_instance = Mock()
        mock_key_info = Mock()
        mock_key_info.key = 'test_key'
        mock_api_keys_instance.key_of.return_value = mock_key_info
        mock_api_keys.return_value = mock_api_keys_instance
        
        mock_chat_model = Mock()
        mock_response = Mock()
        mock_response.content = "Hello! How can I help you?"
        mock_chat_model.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_chat_model
        
        # 创建代理并测试对话
        agent = ChatAgent('test_config.yaml')
        response = agent.chat("Hello")
        
        # 验证
        self.assertEqual(response, "Hello! How can I help you?")
        self.assertEqual(len(agent.chat_history), 3)  # 系统提示 + 用户消息 + AI回复
        mock_chat_model.invoke.assert_called_once()
    
    @patch('multi_agent_framework.chat_agent.load_agent_config')
    @patch('multi_agent_framework.chat_agent.ApiKeys')
    @patch('multi_agent_framework.chat_agent.ChatOpenAI')
    def test_chat_error_handling(self, mock_chat_openai, mock_api_keys, mock_load_config):
        """测试对话错误处理"""
        # 设置模拟
        mock_config = Mock()
        mock_config.config = {}
        mock_load_config.return_value = mock_config
        
        mock_api_keys_instance = Mock()
        mock_key_info = Mock()
        mock_key_info.key = 'test_key'
        mock_api_keys_instance.key_of.return_value = mock_key_info
        mock_api_keys.return_value = mock_api_keys_instance
        
        mock_chat_model = Mock()
        mock_chat_model.invoke.side_effect = Exception("API Error")
        mock_chat_openai.return_value = mock_chat_model
        
        # 创建代理并测试对话
        agent = ChatAgent('test_config.yaml')
        response = agent.chat("Hello")
        
        # 验证错误处理
        self.assertIn("对话出错", response)
        self.assertIn("API Error", response)
    
    @patch('multi_agent_framework.chat_agent.load_agent_config')
    @patch('multi_agent_framework.chat_agent.ApiKeys')
    @patch('multi_agent_framework.chat_agent.ChatOpenAI')
    def test_extract_content_methods(self, mock_chat_openai, mock_api_keys, mock_load_config):
        """测试提取内容的方法"""
        # 设置基础模拟
        mock_config = Mock()
        mock_config.config = {}
        mock_load_config.return_value = mock_config
        
        mock_api_keys_instance = Mock()
        mock_key_info = Mock()
        mock_key_info.key = 'test_key'
        mock_api_keys_instance.key_of.return_value = mock_key_info
        mock_api_keys.return_value = mock_api_keys_instance
        
        mock_chat_openai.return_value = Mock()
        
        agent = ChatAgent('test_config.yaml')
        
        # 测试字符串内容
        result = agent._extract_content("Hello world")
        self.assertEqual(result, "Hello world")
        
        # 测试列表内容
        result = agent._extract_content(["Hello", "world"])
        self.assertEqual(result, "Hello world")
        
        # 测试混合内容
        result = agent._extract_content(["Hello", {"text": "world"}])
        self.assertEqual(result, "Hello world")
        
        # 测试其他类型
        result = agent._extract_content(123)
        self.assertEqual(result, "123")
    
    @patch('multi_agent_framework.chat_agent.load_agent_config')
    @patch('multi_agent_framework.chat_agent.ApiKeys')
    @patch('multi_agent_framework.chat_agent.ChatOpenAI')
    def test_reset_history(self, mock_chat_openai, mock_api_keys, mock_load_config):
        """测试重置历史"""
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
        
        agent = ChatAgent('test_config.yaml')
        
        # 添加一些消息
        agent.chat_history.append(Mock())
        agent.chat_history.append(Mock())
        
        # 重置历史
        agent.reset_history()
        
        # 验证只有系统提示
        self.assertEqual(len(agent.chat_history), 1)
    
    @patch('multi_agent_framework.chat_agent.load_agent_config')
    @patch('multi_agent_framework.chat_agent.ApiKeys')
    @patch('multi_agent_framework.chat_agent.ChatOpenAI')
    def test_save_and_load_conversation(self, mock_chat_openai, mock_api_keys, mock_load_config):
        """测试保存和加载对话"""
        # 设置模拟
        mock_config = Mock()
        mock_config.config = {'model_config': {'provider': 'OpenAI'}}
        mock_load_config.return_value = mock_config
        
        mock_api_keys_instance = Mock()
        mock_key_info = Mock()
        mock_key_info.key = 'test_key'
        mock_api_keys_instance.key_of.return_value = mock_key_info
        mock_api_keys.return_value = mock_api_keys_instance
        
        mock_chat_openai.return_value = Mock()
        
        agent = ChatAgent('test_config.yaml')
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name
        
        try:
            # 保存对话
            agent.save_conversation(temp_file)
            
            # 验证文件存在
            self.assertTrue(os.path.exists(temp_file))
            
            # 加载对话
            agent.load_conversation(temp_file)
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestSimpleChatAgent(unittest.TestCase):
    """测试 SimpleChatAgent 类"""
    
    @patch('multi_agent_framework.simple_chat.load_agent_config')
    @patch('multi_agent_framework.simple_chat.ApiKeys')
    def test_init_success(self, mock_api_keys, mock_load_config):
        """测试成功初始化"""
        # 设置模拟
        mock_config = Mock()
        mock_config.name = 'simple_agent'
        mock_config.config = {
            'model_config': {
                'provider': 'OpenAI',
                'model': 'gpt-3.5-turbo'
            },
            'system_prompt': 'You are helpful.'
        }
        mock_load_config.return_value = mock_config
        mock_api_keys.return_value = Mock()
        
        # 创建代理
        agent = SimpleChatAgent('test_config.yaml')
        
        # 验证
        self.assertEqual(agent.config_path, 'test_config.yaml')
        self.assertEqual(agent.config, mock_config)
        self.assertEqual(len(agent.chat_history), 1)  # 系统提示
        self.assertEqual(agent.chat_history[0]['role'], 'system')
        self.assertEqual(agent.chat_history[0]['content'], 'You are helpful.')
    
    @patch('multi_agent_framework.simple_chat.load_agent_config')
    @patch('multi_agent_framework.simple_chat.ApiKeys')
    def test_chat_functionality(self, mock_api_keys, mock_load_config):
        """测试对话功能"""
        # 设置模拟
        mock_config = Mock()
        mock_config.name = 'simple_agent'
        mock_config.config = {'system_prompt': 'You are helpful.'}
        mock_load_config.return_value = mock_config
        mock_api_keys.return_value = Mock()
        
        agent = SimpleChatAgent('test_config.yaml')
        
        # 测试对话
        response = agent.chat("Hello")
        
        # 验证
        self.assertIn("simple_agent", response)
        self.assertIn("Hello", response)
        self.assertEqual(len(agent.chat_history), 3)  # 系统提示 + 用户消息 + AI回复
        self.assertEqual(agent.chat_history[1]['role'], 'user')
        self.assertEqual(agent.chat_history[1]['content'], 'Hello')
        self.assertEqual(agent.chat_history[2]['role'], 'assistant')
    
    @patch('multi_agent_framework.simple_chat.load_agent_config')
    @patch('multi_agent_framework.simple_chat.ApiKeys')
    def test_get_api_key_openai(self, mock_api_keys, mock_load_config):
        """测试获取 OpenAI API 密钥"""
        # 设置模拟
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
        mock_key_info.key = 'test_api_key'
        mock_api_keys_instance.key_of.return_value = mock_key_info
        mock_api_keys.return_value = mock_api_keys_instance
        
        agent = SimpleChatAgent('test_config.yaml')
        api_key = agent.get_api_key()
        
        # 验证
        self.assertEqual(api_key, 'test_api_key')
        mock_api_keys_instance.key_of.assert_called_once_with('openai')
    
    @patch('multi_agent_framework.simple_chat.load_agent_config')
    @patch('multi_agent_framework.simple_chat.ApiKeys')
    def test_get_api_key_deepseek(self, mock_api_keys, mock_load_config):
        """测试获取 DeepSeek API 密钥"""
        # 设置模拟
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
        
        # 验证
        self.assertEqual(api_key, 'test_deepseek_key')
        mock_api_keys_instance.key_of.assert_called_once_with('deepseek-chat')
    
    @patch('multi_agent_framework.simple_chat.load_agent_config')
    @patch('multi_agent_framework.simple_chat.ApiKeys')
    def test_get_api_key_error(self, mock_api_keys, mock_load_config):
        """测试获取 API 密钥失败"""
        # 设置模拟
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
        
        # 验证异常
        with self.assertRaises(ValueError):
            agent.get_api_key()
    
    @patch('multi_agent_framework.simple_chat.load_agent_config')
    @patch('multi_agent_framework.simple_chat.ApiKeys')
    def test_history_operations(self, mock_api_keys, mock_load_config):
        """测试历史操作"""
        # 设置模拟
        mock_config = Mock()
        mock_config.config = {'system_prompt': 'You are helpful.'}
        mock_load_config.return_value = mock_config
        mock_api_keys.return_value = Mock()
        
        agent = SimpleChatAgent('test_config.yaml')
        
        # 测试获取历史
        history = agent.get_history()
        self.assertEqual(len(history), 1)  # 只有系统提示
        self.assertIsNot(history, agent.chat_history)  # 确保是副本
        
        # 添加对话
        agent.chat("Hello")
        self.assertEqual(len(agent.chat_history), 3)
        
        # 测试重置历史
        agent.reset_history()
        self.assertEqual(len(agent.chat_history), 1)
        self.assertEqual(agent.chat_history[0]['role'], 'system')
    
    @patch('multi_agent_framework.simple_chat.load_agent_config')
    @patch('multi_agent_framework.simple_chat.ApiKeys')
    def test_save_and_load_conversation(self, mock_api_keys, mock_load_config):
        """测试保存和加载对话"""
        # 设置模拟
        mock_config = Mock()
        mock_config.config = {'model_config': {'provider': 'OpenAI'}}
        mock_load_config.return_value = mock_config
        mock_api_keys.return_value = Mock()
        
        agent = SimpleChatAgent('test_config.yaml')
        
        # 添加消息
        agent.chat("Hello")
        original_history = agent.get_history()
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name
        
        try:
            # 保存对话
            agent.save_conversation(temp_file)
            
            # 验证文件存在
            self.assertTrue(os.path.exists(temp_file))
            
            # 重置历史
            agent.reset_history()
            
            # 加载对话
            agent.load_conversation(temp_file)
            
            # 验证历史恢复
            loaded_history = agent.get_history()
            self.assertEqual(len(loaded_history), len(original_history))
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestInteractiveChatAgent(unittest.TestCase):
    """测试 InteractiveChatAgent 类"""
    
    @patch('multi_agent_framework.chat_agent.ChatAgent')
    def test_init(self, mock_chat_agent):
        """测试初始化"""
        # 创建交互式代理
        interactive_agent = InteractiveChatAgent('test_config.yaml')
        
        # 验证
        self.assertIsNotNone(interactive_agent.agent)
        mock_chat_agent.assert_called_once_with('test_config.yaml', 'api_keys.yaml')


def run_tests():
    """运行所有测试"""
    print("🧪 开始运行聊天代理测试...")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestChatAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestSimpleChatAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestInteractiveChatAgent))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n📊 测试结果:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ 错误的测试:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 部分测试失败")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 