import logging
from .graph_agent import GraphAgent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

# 导入并设置日志
from . import logging_utils
logging_utils.setup_logging(logging.INFO)

logger = logging.getLogger(__name__)


def interactive_graph_chat():
    """使用 LangGraph 代理进行交互式对话"""
    config_path = "configs/agent/example.yaml"
    
    try:
        agent = GraphAgent(config_path)
        logger.info(f"代理 '{agent.config.name}' 已加载。")
        print("\n--- 对话开始 ---")
        print("输入 'quit' 或 'exit' 退出。")
        
        history: list[BaseMessage] = []
        
        while True:
            user_input = input("你: ").strip()
            if user_input.lower() in ["quit", "exit"]:
                print("--- 对话结束 ---")
                break
                
            if not user_input:
                continue

            response_content = agent.chat(user_input, history)
            
            print(f"AI: {response_content}")
            
            # 更新历史
            history.append(HumanMessage(content=user_input))
            history.append(AIMessage(content=response_content))

    except Exception as e:
        logger.error(f"发生致命错误: {e}", exc_info=True)
        print(f"\n❌ 代理运行时出现问题，请查看日志了解详情。")


if __name__ == "__main__":
    interactive_graph_chat()
