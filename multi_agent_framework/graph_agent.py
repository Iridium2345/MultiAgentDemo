"""
基于 LangGraph 的代理实现
"""

import logging
from typing import List, TypedDict, Any, Dict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langgraph.graph import END, StateGraph

from .api_keys import ApiKeys
from .config.loader import load_agent_config
from .tool_manager import ToolManager

# 初始化日志记录器
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """
    定义 LangGraph 的状态。
    
    Attributes:
        messages: 对话消息列表，用于在图的节点之间传递。
    """
    messages: List[BaseMessage]


class GraphAgent:
    """
    一个基于 LangGraph 的对话代理，具备动态工具调用能力。
    
    这个代理使用一个图来处理对话流程：
    1.  调用语言模型获取回复或工具调用请求。
    2.  如果模型请求调用工具，则执行工具并将结果返回给模型。
    3.  如果模型提供最终回复，则结束流程。
    """

    def __init__(self, config_path: str, api_keys_path: str = "api_keys.yaml"):
        """
        初始化代理。
        
        Args:
            config_path: 代理配置文件的路径。
            api_keys_path: API 密钥文件的路径。
        """
        logger.info(f"正在从 {config_path} 初始化 GraphAgent...")
        self.config = load_agent_config(config_path)
        self.api_keys = ApiKeys(api_keys_path)
        
        # 初始化工具管理器
        tool_config_paths = [f"configs/tools/{name}.yaml" for name in self.config.tools]
        self.tool_manager = ToolManager(tool_config_paths)
        
        # 初始化聊天模型并绑定工具
        self.llm = self._init_chat_model()
        
        # 构建并编译图
        self.graph = self._build_graph()
        logger.info("GraphAgent 初始化完成。")

    def _init_chat_model(self) -> Any:
        """根据配置文件初始化并返回一个 ChatOpenAI 实例。"""
        model_config = self.config.config.get('model_config', {})
        provider = model_config.get('provider', 'OpenAI')
        model = model_config.get('model', 'gpt-3.5-turbo')
        logger.info(f"正在初始化模型: {provider}/{model}")
        
        api_key_name = model.lower() if provider.lower() == 'deepseek' else provider.lower()
        
        try:
            api_key_info = self.api_keys.key_of(api_key_name)
            api_key = SecretStr(api_key_info.key)
            base_url = api_key_info.base_url or None
        except KeyError:
            logger.error(f"未找到 {api_key_name} 的 API 密钥")
            raise ValueError(f"未找到 {api_key_name} 的API密钥")

        # 将工具 schema 转换为 LangChain 工具并绑定到模型
        tools = self.tool_manager.get_langchain_tools()  # type: ignore
        logger.info(f"向模型绑定 {len(tools)} 个工具: {[t.name for t in tools]}")  # type: ignore
        return ChatOpenAI(
            model=model, 
            api_key=api_key, 
            base_url=base_url,
            temperature=model_config.get('temperature', 0.7)
        ).bind_tools(tools)  # type: ignore

    def _agent_node(self, state: AgentState) -> Dict[str, Any]:
        """图中调用语言模型的节点。"""
        logger.debug("调用 Agent 节点...")
        messages = state['messages']
        
        # 为了兼容 DeepSeek API，我们需要确保 ToolMessage 总是紧跟在包含 tool_calls 的 AIMessage 之后
        # 如果存在 ToolMessage，我们需要重新构建消息序列
        cleaned_messages = []
        i = 0
        while i < len(messages):
            msg = messages[i]
            if isinstance(msg, ToolMessage):
                # 跳过 ToolMessage，因为它们会导致 DeepSeek API 错误
                # 我们将在工具调用完成后手动处理结果
                i += 1
                continue
            cleaned_messages.append(msg)
            i += 1
        
        response = self.llm.invoke(cleaned_messages)
        return {"messages": [response]}

    def _tool_node(self, state: AgentState) -> Dict[str, Any]:
        """图中执行工具的节点。"""
        logger.debug("调用 Tool 节点...")
        ai_message = state['messages'][-1]
        tool_results = []
        
        # 执行所有工具调用
        for tool_call in ai_message.tool_calls:  # type: ignore
            logger.info(f"执行工具调用: {tool_call['name']}，参数: {tool_call['args']}")
            result = self.tool_manager.run_tool(tool_call['name'], **tool_call['args'])  # type: ignore
            tool_results.append(f"工具 {tool_call['name']} 的结果: {result}")  # type: ignore
        
        # 创建一个包含工具结果的 AI 消息，而不是 ToolMessage
        # 这样可以避免 DeepSeek API 的消息格式限制
        combined_result = "\n".join(tool_results)  # type: ignore
        response_message = AIMessage(content=f"基于工具调用的结果:\n{combined_result}\n\n让我为您总结一下这些信息。")
        
        return {"messages": [response_message]}

    def _router(self, state: AgentState) -> str:
        """决定下一步走向的路由器。"""
        logger.debug("调用 Router 节点...")
        last_message = state['messages'][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            logger.info("路由决策: 调用工具。")
            return "call_tool"
        logger.info("路由决策: 结束。")
        return "end"

    def _build_graph(self) -> Any:
        """构建并编译 LangGraph。"""
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("action", self._tool_node)
        
        workflow.set_entry_point("agent")
        
        workflow.add_conditional_edges(
            "agent",
            self._router,
            {"call_tool": "action", "end": END}
        )
        # 工具执行完成后直接结束，不再回到 agent 节点
        workflow.add_edge("action", END)
        
        return workflow.compile()

    def chat(self, user_message: str, history: List[BaseMessage]) -> str:
        """
        与代理进行一次对话。
        
        Args:
            user_message: 用户的输入消息。
            history: 当前的对话历史。
            
        Returns:
            AI 的回复消息。
        """
        system_prompt = self.config.config.get('system_prompt', '')
        messages: List[BaseMessage] = []

        # 如果历史中没有系统提示，则添加它
        if system_prompt and not any(isinstance(m, SystemMessage) for m in history):
            logger.debug(f"添加系统提示: {system_prompt}")
            messages.append(SystemMessage(content=system_prompt))
        
        # 添加现有历史
        if history:
            messages.extend(history)
            
        # 添加当前用户消息
        messages.append(HumanMessage(content=user_message))
        
        logger.info("正在调用 LangGraph...")
        final_state = self.graph.invoke({"messages": messages})
        
        # 从结果中提取AI回复
        ai_response = final_state['messages'][-1]
        response_content = ai_response.content if isinstance(ai_response, AIMessage) else str(ai_response)
        logger.info(f"GraphAgent 回复: {response_content}")
        return response_content 