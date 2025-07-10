"""
简化版本的对话代理实现
"""

import logging
import yaml
from typing import Dict, List

from .api_keys import ApiKeys
from .config.loader import load_agent_config

# 初始化日志记录器
logger = logging.getLogger(__name__)


class SimpleChatAgent:
    """
    一个简化的对话代理，用于快速演示和测试。
    
    这个代理不使用 LangGraph，而是通过一个简单循环来处理对话。
    它不实际调用 LLM，而是模拟一个回复。
    """
    
    def __init__(self, config_path: str, api_keys_path: str = "api_keys.yaml") -> None:
        """初始化对话代理"""
        logger.info(f"正在从 {config_path} 初始化 SimpleChatAgent...")
        self.config_path = config_path
        
        # 加载配置
        self.config = load_agent_config(config_path)
        
        # 加载API密钥
        self.api_keys = ApiKeys(api_keys_path)
        
        # 获取配置信息
        self.model_config = self.config.config.get('model_config', {})
        self.system_prompt = self.config.config.get('system_prompt', '')
        self.base_url = self.get_base_url()
        
        # 对话历史
        self.chat_history: List[Dict[str, str]] = []
        
        # 如果有系统提示，添加到历史
        if self.system_prompt:
            self.chat_history.append({"role": "system", "content": self.system_prompt})
        
        logger.info("SimpleChatAgent 初始化完成。")
        logger.info(f"模型配置: {self.model_config}")
        logger.debug(f"系统提示: {self.system_prompt}")
        logger.info(f"基础URL: {self.base_url}")
    
    def get_api_key(self) -> str:
        """获取API密钥"""
        provider = self.model_config.get('provider', 'OpenAI')
        model = self.model_config.get('model', 'gpt-3.5-turbo')
        
        # 根据provider获取API密钥
        api_key_name = model.lower() if provider.lower() == 'deepseek' else provider.lower()
        
        try:
            api_key_info = self.api_keys.key_of(api_key_name)
            return api_key_info.key
        except KeyError:
            raise ValueError(f"未找到 {api_key_name} 的API密钥")
    
    def get_base_url(self) -> str:
        """获取API基础URL"""
        provider = self.model_config.get('provider', 'OpenAI')
        model = self.model_config.get('model', 'gpt-3.5-turbo')
        
        # 根据provider获取API密钥配置
        api_key_name = model.lower() if provider.lower() == 'deepseek' else provider.lower()
        
        try:
            api_key_info = self.api_keys.key_of(api_key_name)
            return api_key_info.base_url
        except KeyError:
            # 如果找不到，返回空字符串而不是抛出错误
            return ""
    
    def chat(self, message: str) -> str:
        """
        模拟对话功能
        """
        # 添加用户消息
        self.chat_history.append({"role": "user", "content": message})
        
        # 模拟AI回复（实际应用中这里会调用LLM API）
        response = f"我是 {self.config.name}，我收到了您的消息：{message}"
        
        # 添加AI回复
        self.chat_history.append({"role": "assistant", "content": response})
        
        return response
    
    def reset_history(self) -> None:
        """重置对话历史"""
        self.chat_history = []
        if self.system_prompt:
            self.chat_history.append({"role": "system", "content": self.system_prompt})
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.chat_history.copy()
    
    def save_conversation(self, file_path: str) -> None:
        """保存对话到文件"""
        conversation_data = {
            "config": self.config_path,
            "model": self.model_config,
            "history": self.chat_history
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(conversation_data, f, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"对话已保存到 {file_path}")
    
    def load_conversation(self, file_path: str) -> None:
        """从文件加载对话"""
        logger.info(f"正在从 {file_path} 加载对话...")
        with open(file_path, 'r', encoding='utf-8') as f:
            conversation_data = yaml.safe_load(f)
        
        self.chat_history = conversation_data.get('history', [])
        logger.info(f"对话已从 {file_path} 加载")


def interactive_chat_demo() -> None:
    """交互式对话演示"""
    config_path = "configs/agent/example.yaml"
    
    try:
        # 创建对话代理
        agent = SimpleChatAgent(config_path)
        
        print("\n--- 交互式对话演示 (简化版) ---")
        print("输入 'quit' 或 'exit' 退出对话")
        print("输入 'reset' 重置对话历史")
        print("输入 'history' 查看对话历史")
        print("输入 'save <filename>' 保存对话")
        print("=" * 30)
        
        while True:
            try:
                user_input = input("\n用户: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("--- 对话结束 ---")
                    break
                
                elif user_input.lower() == 'reset':
                    agent.reset_history()
                    print("对话历史已重置")
                    continue
                
                elif user_input.lower() == 'history':
                    history = agent.get_history()
                    print("\n--- 对话历史 ---")
                    for i, msg in enumerate(history, 1):
                        print(f"{i}. {msg['role']}: {msg['content']}")
                    print("=" * 20)
                    continue
                
                elif user_input.lower().startswith('save '):
                    filename = user_input[5:].strip()
                    if filename:
                        agent.save_conversation(filename)
                    else:
                        print("请提供文件名")
                    continue
                
                elif not user_input:
                    continue
                
                # 获取AI回复
                response = agent.chat(user_input)
                print(f"\nAI: {response}")
                
            except KeyboardInterrupt:
                print("\n\n--- 对话结束 ---")
                break
            except Exception as e:
                logger.error(f"交互式会话出错: {e}", exc_info=True)
                print(f"出现错误: {e}")
                
    except Exception as e:
        logger.error(f"代理初始化失败: {e}", exc_info=True)
        print(f"初始化失败: {e}")


if __name__ == "__main__":
    interactive_chat_demo() 