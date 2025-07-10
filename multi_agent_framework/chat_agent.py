"""
基于 langchain 的对话代理实现
"""

import logging
import yaml
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from pydantic import SecretStr

from .api_keys import ApiKeys
from .config.loader import load_agent_config

# 初始化日志记录器
logger = logging.getLogger(__name__)


class ChatAgent:
    """
    一个基于 LangChain 的传统对话代理。
    
    这个代理不使用 LangGraph，而是直接管理对话历史并调用模型。
    """
    
    def __init__(self, config_path: str, api_keys_path: str = "api_keys.yaml"):
        """
        初始化对话代理
        
        Args:
            config_path: 代理配置文件路径
            api_keys_path: API密钥文件路径
        """
        logger.info(f"正在从 {config_path} 初始化 ChatAgent...")
        self.config_path = config_path
        self.api_keys_path = api_keys_path
        
        # 加载配置
        self.config = load_agent_config(config_path)
        
        # 加载API密钥
        self.api_keys = ApiKeys(api_keys_path)
        
        # 初始化聊天模型
        self.chat_model = self._init_chat_model()
        
        # 初始化对话历史
        self.chat_history: List[BaseMessage] = []
        
        # 设置系统提示
        system_prompt = self.config.config.get('system_prompt')
        if system_prompt:
            self.chat_history.append(SystemMessage(content=system_prompt))
        
        logger.info("ChatAgent 初始化完成。")
    
    def _init_chat_model(self) -> ChatOpenAI:
        """初始化聊天模型"""
        # 获取模型配置
        model_config = self.config.config.get('model_config', {})
        provider = model_config.get('provider', 'OpenAI')
        model = model_config.get('model', 'gpt-3.5-turbo')
        temperature = model_config.get('temperature', 0.7)
        max_tokens = model_config.get('max_tokens', 1000)
        
        # 根据provider获取API密钥
        api_key_name = model.lower() if provider.lower() == 'deepseek' else provider.lower()
        
        try:
            api_key_info = self.api_keys.key_of(api_key_name)
            api_key = SecretStr(api_key_info.key)
            base_url = api_key_info.base_url or None
        except KeyError:
            logger.error(f"未找到 {api_key_name} 的API密钥")
            raise ValueError(f"未找到 {api_key_name} 的API密钥")
        
        # 创建ChatOpenAI实例
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            api_key=api_key,
            base_url=base_url
        )
    
    def chat(self, message: str) -> str:
        """
        进行对话
        
        Args:
            message: 用户消息
            
        Returns:
            AI回复
        """
        # 添加用户消息到历史
        self.chat_history.append(HumanMessage(content=message))
        
        try:
            logger.info("正在调用 ChatModel...")
            response = self.chat_model.invoke(self.chat_history)
            
            # 确保响应内容是字符串
            response_content = self._extract_content(response.content)  # type: ignore
            
            # 添加AI回复到历史
            self.chat_history.append(AIMessage(content=response_content))
            
            logger.info(f"ChatAgent 回复: {response_content}")
            return response_content
        
        except Exception as e:
            logger.error(f"对话出错: {e}", exc_info=True)
            error_msg = f"对话出错: {str(e)}"
            return error_msg
    
    def _extract_content(self, content: Any) -> str:
        """提取响应内容，确保返回字符串"""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # 如果是列表，尝试连接所有字符串元素
            text_parts: List[str] = []
            for item in content:  # type: ignore
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict):
                    # 如果是字典，尝试提取text字段
                    text_parts.append(str(item.get('text', item)))  # type: ignore
                else:
                    text_parts.append(str(item))  # type: ignore
            return ' '.join(text_parts)
        else:
            return str(content)
    
    def reset_history(self):
        """重置对话历史"""
        self.chat_history = []
        # 重新设置系统提示
        system_prompt = self.config.config.get('system_prompt')
        if system_prompt:
            self.chat_history.append(SystemMessage(content=system_prompt))
        logger.info("对话历史已重置。")
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        history: List[Dict[str, str]] = []
        for message in self.chat_history:
            if isinstance(message, HumanMessage):
                history.append({"role": "user", "content": self._extract_content(message.content)})  # type: ignore
            elif isinstance(message, AIMessage):
                history.append({"role": "assistant", "content": self._extract_content(message.content)})  # type: ignore
            elif isinstance(message, SystemMessage):
                history.append({"role": "system", "content": self._extract_content(message.content)})  # type: ignore
        return history
    
    def save_conversation(self, file_path: str):
        """保存对话到文件"""
        conversation_data = {
            "config": self.config_path,
            "model": self.config.config.get('model_config', {}),
            "history": self.get_history()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(conversation_data, f, allow_unicode=True, default_flow_style=False)
        logger.info(f"对话已保存到 {file_path}")
    
    def load_conversation(self, file_path: str):
        """从文件加载对话"""
        logger.info(f"正在从 {file_path} 加载对话...")
        with open(file_path, 'r', encoding='utf-8') as f:
            conversation_data = yaml.safe_load(f)
        
        # 重置历史并加载
        self.chat_history = []
        for msg in conversation_data.get('history', []):
            role = msg.get('role')
            content = msg.get('content')
            
            if role == 'user':
                self.chat_history.append(HumanMessage(content=content))
            elif role == 'assistant':
                self.chat_history.append(AIMessage(content=content))
            elif role == 'system':
                self.chat_history.append(SystemMessage(content=content))
        logger.info("对话已从文件加载。")
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置信息"""
        return {
            "name": self.config.name,
            "description": self.config.description,
            "model_config": self.config.config.get('model_config', {}),
            "system_prompt": self.config.config.get('system_prompt', ''),
            "tools": self.config.tools,
            "knowledge_bases": self.config.knowledge_bases
        }


class InteractiveChatAgent:
    """交互式对话代理"""
    
    def __init__(self, config_path: str, api_keys_path: str = "api_keys.yaml"):
        """初始化交互式对话代理"""
        self.agent = ChatAgent(config_path, api_keys_path)
        
    def start_interactive_chat(self):
        """启动交互式对话"""
        config_info = self.agent.get_config_info()
        
        print("--- 对话代理启动 ---")
        print(f"代理名称: {config_info['name']}")
        print(f"描述: {config_info['description']}")
        print(f"模型配置: {config_info['model_config']}")
        print(f"系统提示: {config_info['system_prompt']}")
        print("\n命令:")
        print("  'quit' 或 'exit' - 退出对话")
        print("  'reset' - 重置对话历史")
        print("  'history' - 查看对话历史")
        print("  'save <filename>' - 保存对话")
        print("  'load <filename>' - 加载对话")
        print("  'info' - 查看配置信息")
        print("=" * 40)
        
        while True:
            try:
                user_input = input("\n用户: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("--- 对话结束 ---")
                    break
                
                elif user_input.lower() == 'reset':
                    self.agent.reset_history()
                    print("对话历史已重置")
                    continue
                
                elif user_input.lower() == 'history':
                    history = self.agent.get_history()
                    print("\n--- 对话历史 ---")
                    for i, msg in enumerate(history, 1):
                        print(f"{i}. {msg['role']}: {msg['content']}")
                    print("=" * 20)
                    continue
                
                elif user_input.lower() == 'info':
                    config_info = self.agent.get_config_info()
                    print("\n--- 配置信息 ---")
                    for key, value in config_info.items():
                        print(f"{key}: {value}")
                    print("=" * 20)
                    continue
                
                elif user_input.lower().startswith('save '):
                    filename = user_input[5:].strip()
                    if filename:
                        self.agent.save_conversation(filename)
                        print(f"对话已保存到 {filename}")
                    else:
                        print("错误: 请提供文件名")
                    continue
                
                elif user_input.lower().startswith('load '):
                    filename = user_input[5:].strip()
                    if filename:
                        try:
                            self.agent.load_conversation(filename)
                            print(f"对话已从 {filename} 加载")
                        except Exception as e:
                            print(f"加载失败: {e}")
                    else:
                        print("错误: 请提供文件名")
                    continue
                
                elif not user_input:
                    continue
                
                # 获取AI回复
                response = self.agent.chat(user_input)
                print(f"\nAI: {response}")
                
            except KeyboardInterrupt:
                print("\n\n--- 对话结束 ---")
                break
            except Exception as e:
                logger.error(f"交互式会话出错: {e}", exc_info=True)
                print(f"错误: {e}") 