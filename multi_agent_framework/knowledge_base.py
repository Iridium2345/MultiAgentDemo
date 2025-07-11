"""
知识库接口模块
提供通用的知识库操作接口和基础数据模型
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class KnowledgeType(Enum):
    """知识库类型枚举"""
    CHROMA = "chroma"
    FAISS = "faiss"
    PINECONE = "pinecone"
    
    @classmethod
    def from_string(cls, value: str) -> "KnowledgeType":
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"不支持的知识库类型: {value}，支持的类型: {[t.value for t in cls]}")

@dataclass
class KnowledgeItem:
    """知识项数据模型"""
    id: str
    content: str
    title: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    embedding: Optional[List[float]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SearchResult:
    """搜索结果数据模型"""
    item: KnowledgeItem
    score: float
    rank: int

class KnowledgeBase(ABC):
    """
    知识库抽象基类
    定义所有知识库实现必须支持的基本操作
    """
    
    @abstractmethod
    def add_item(self, item: KnowledgeItem) -> bool:
        """
        添加知识项到知识库
        
        Args:
            item: 要添加的知识项
            
        Returns:
            是否添加成功
        """
        pass
    
    @abstractmethod
    def get_item(self, item_id: str) -> Optional[KnowledgeItem]:
        """
        根据ID获取知识项
        
        Args:
            item_id: 知识项ID
            
        Returns:
            知识项对象，如果不存在则返回None
        """
        pass
    
    @abstractmethod
    def search(self, query: str, top_k: int = 10, filter_dict: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """
        语义搜索知识项
        
        Args:
            query: 搜索查询
            top_k: 返回的最大结果数
            filter_dict: 过滤条件
            
        Returns:
            搜索结果列表
        """
        pass
    
    @abstractmethod
    def update_item(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新知识项
        
        Args:
            item_id: 要更新的知识项ID
            updates: 更新的字段和值
            
        Returns:
            是否更新成功
        """
        pass
    
    @abstractmethod
    def delete_item(self, item_id: str) -> bool:
        """
        删除知识项
        
        Args:
            item_id: 要删除的知识项ID
            
        Returns:
            是否删除成功
        """
        pass
    
    @abstractmethod
    def list_items(self, category: Optional[str] = None, tags: Optional[List[str]] = None, 
                   limit: int = 100, offset: int = 0) -> List[KnowledgeItem]:
        """
        列出知识项
        
        Args:
            category: 类别过滤
            tags: 标签过滤
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            知识项列表
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息字典
        """
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """
        清空知识库
        
        Returns:
            是否清空成功
        """
        pass 