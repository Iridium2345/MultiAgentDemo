"""
中央日志配置
"""
import logging
import sys

def setup_logging(level=logging.INFO):
    """
    配置全局日志记录器
    
    Args:
        level: 日志级别 (e.g., logging.INFO, logging.DEBUG)
    """
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 如果已经有处理器，则先移除，防止重复输出
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    # 创建一个格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建一个流处理器，将日志输出到控制台
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    # 将处理器添加到根日志记录器
    root_logger.addHandler(stream_handler)

# 在模块加载时设置默认日志记录
setup_logging() 