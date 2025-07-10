"""
测试聊天代理模块
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import Mock, patch

# 模拟langchain依赖
sys.modules['langchain_openai'] = Mock()
sys.modules['langchain_core.messages'] = Mock()
sys.modules['pydantic'] = Mock()

from multi_agent_framework.chat_agent import ChatAgent, InteractiveChatAgent
from multi_agent_framework.simple_chat import SimpleChatAgent


class TestChatAgent(unittest.TestCase):
    """测试 ChatAgent 类"""
    
    def setUp(self) -> None:
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
        
        self.api_keys_data = {
            'openai': {
                'key': 'test_openai_key',
                'description': 'Test OpenAI key'
            },
            'deepseek': {
                'key': 'test_deepseek_key',
                'description': 'Test DeepSeek key'
            }
        }
    
    @patch('multi_agent_framework.chat_agent.load_agent_config')
    @patch('multi_agent_framework.chat_agent.ApiKeys')
    @patch('multi_agent_framework.chat_agent.ChatOpenAI')
    def test_init_success(self, mock_chat_openai: Mock, mock_api_keys: Mock, mock_load_config: Mock) -> None:
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
    def test_init_missing_api_key(self, mock_api_keys: Mock, mock_load_config: Mock) -> None:
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
    def test_chat_success(self, mock_chat_openai: Mock, mock_api_keys: Mock, mock_load_config: Mock) -> None:
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
    def test_chat_error_handling(self, mock_chat_openai: Mock, mock_api_keys: Mock, mock_load_config: Mock) -> None:
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
    def test_reset_history(self, mock_chat_openai: Mock, mock_api_keys: Mock, mock_load_config: Mock) -> None:
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
    def test_save_and_load_conversation(self, mock_chat_openai: Mock, mock_api_keys: Mock, mock_load_config: Mock) -> None:
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
    
    @patch('multi_agent_framework.chat_agent.load_agent_config')
    @patch('multi_agent_framework.chat_agent.ApiKeys')
    @patch('multi_agent_framework.chat_agent.ChatOpenAI')
    def test_get_config_info(self, mock_chat_openai: Mock, mock_api_keys: Mock, mock_load_config: Mock) -> None:
        """测试获取配置信息"""
        # 设置模拟
        mock_config = Mock()
        mock_config.name = 'test_agent'
        mock_config.description = 'Test description'
        mock_config.config = {
            'model_config': {'provider': 'OpenAI'},
            'system_prompt': 'You are helpful.'
        }
        mock_config.tools = ['tool1']
        mock_config.knowledge_bases = ['kb1']
        mock_load_config.return_value = mock_config
        
        mock_api_keys_instance = Mock()
        mock_key_info = Mock()
        mock_key_info.key = 'test_key'
        mock_api_keys_instance.key_of.return_value = mock_key_info
        mock_api_keys.return_value = mock_api_keys_instance
        
        mock_chat_openai.return_value = Mock()
        
        agent = ChatAgent('test_config.yaml')
        config_info = agent.get_config_info()
        
        # 验证配置信息
        self.assertEqual(config_info['name'], 'test_agent')
        self.assertEqual(config_info['description'], 'Test description')
        self.assertEqual(config_info['model_config'], {'provider': 'OpenAI'})
        self.assertEqual(config_info['system_prompt'], 'You are helpful.')
        self.assertEqual(config_info['tools'], ['tool1'])
        self.assertEqual(config_info['knowledge_bases'], ['kb1'])


class TestSimpleChatAgent(unittest.TestCase):
    """测试 SimpleChatAgent 类"""
    
    def setUp(self) -> None:
        """设置测试环境"""
        self.config_data = {
            'name': 'simple_agent',
            'description': 'Simple test agent',
            'config': {
                'model_config': {
                    'provider': 'OpenAI',
                    'model': 'gpt-3.5-turbo'
                },
                'system_prompt': 'You are a simple assistant.'
            },
            'tools': [],
            'knowledge_bases': []
        }
    
    @patch('multi_agent_framework.simple_chat.load_agent_config')
    @patch('multi_agent_framework.simple_chat.ApiKeys')
    def test_init_success(self, mock_api_keys: Mock, mock_load_config: Mock) -> None:
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
    def test_chat_functionality(self, mock_api_keys: Mock, mock_load_config: Mock) -> None:
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
    def test_get_api_key_success(self, mock_api_keys: Mock, mock_load_config: Mock) -> None:
        """测试成功获取 API 密钥"""
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
    def test_get_api_key_deepseek(self, mock_api_keys: Mock, mock_load_config: Mock) -> None:
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
    def test_get_api_key_error(self, mock_api_keys: Mock, mock_load_config: Mock) -> None:
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
    def test_reset_history(self, mock_api_keys: Mock, mock_load_config: Mock) -> None:
        """测试重置历史"""
        # 设置模拟
        mock_config = Mock()
        mock_config.config = {'system_prompt': 'You are helpful.'}
        mock_load_config.return_value = mock_config
        mock_api_keys.return_value = Mock()
        
        agent = SimpleChatAgent('test_config.yaml')
        
        # 添加消息
        agent.chat("Hello")
        self.assertEqual(len(agent.chat_history), 3)
        
        # 重置历史
        agent.reset_history()
        
        # 验证只有系统提示
        self.assertEqual(len(agent.chat_history), 1)
        self.assertEqual(agent.chat_history[0]['role'], 'system')
    
    @patch('multi_agent_framework.simple_chat.load_agent_config')
    @patch('multi_agent_framework.simple_chat.ApiKeys')
    def test_get_history(self, mock_api_keys: Mock, mock_load_config: Mock) -> None:
        """测试获取历史"""
        # 设置模拟
        mock_config = Mock()
        mock_config.config = {}
        mock_load_config.return_value = mock_config
        mock_api_keys.return_value = Mock()
        
        agent = SimpleChatAgent('test_config.yaml')
        
        # 添加消息
        agent.chat("Hello")
        
        # 获取历史
        history = agent.get_history()
        
        # 验证历史是副本
        self.assertEqual(len(history), 2)  # 用户消息 + AI回复
        self.assertIsNot(history, agent.chat_history)
        self.assertEqual(history[0]['role'], 'user')
        self.assertEqual(history[1]['role'], 'assistant')
    
    @patch('multi_agent_framework.simple_chat.load_agent_config')
    @patch('multi_agent_framework.simple_chat.ApiKeys')
    def test_save_and_load_conversation(self, mock_api_keys: Mock, mock_load_config: Mock) -> None:
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
    def test_init(self, mock_chat_agent: Mock) -> None:
        """测试初始化"""
        # 创建交互式代理
        interactive_agent = InteractiveChatAgent('test_config.yaml')
        
        # 验证
        self.assertIsNotNone(interactive_agent.agent)
        mock_chat_agent.assert_called_once_with('test_config.yaml', 'api_keys.yaml')


def run_tests() -> bool:
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestChatAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestSimpleChatAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestInteractiveChatAgent))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 