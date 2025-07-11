"""
知识库管理器
负责管理和协调不同类型的知识库
"""

import logging
from typing import Dict, Any, List, Optional
from .knowledge_base import KnowledgeBase, KnowledgeItem, SearchResult, KnowledgeType
from .knowledge_bases import ChromaKnowledgeBase
from .config.knowledge_config import KnowledgeBaseConfig

logger = logging.getLogger(__name__)

class KnowledgeManager:
    """
    知识库管理器
    负责管理多个知识库实例，提供统一的接口
    """
    
    def __init__(self):
        """初始化知识库管理器"""
        self.knowledge_bases: Dict[str, KnowledgeBase] = {}
        self.configs: Dict[str, KnowledgeBaseConfig] = {}
        logger.info("知识库管理器已初始化")
    
    def add_knowledge_base(self, name: str, config: KnowledgeBaseConfig) -> bool:
        """
        添加知识库
        
        Args:
            name: 知识库名称
            config: 知识库配置
            
        Returns:
            是否添加成功
        """
        try:
            if not config.enable:
                logger.info(f"知识库 {name} 已禁用，跳过初始化")
                return False
            
            # 根据类型创建知识库实例
            if config.type == KnowledgeType.CHROMA:
                knowledge_base = self._create_chroma_knowledge_base(config)
            else:
                logger.error(f"不支持的知识库类型: {config.type}")
                return False
            
            self.knowledge_bases[name] = knowledge_base
            self.configs[name] = config
            logger.info(f"成功添加知识库: {name} (类型: {config.type.value})")
            return True
            
        except Exception as e:
            logger.error(f"添加知识库失败 {name}: {e}")
            return False
    
    def _create_chroma_knowledge_base(self, config: KnowledgeBaseConfig) -> ChromaKnowledgeBase:
        """创建 Chroma 知识库实例"""
        connection_info = config.connection_info
        
        return ChromaKnowledgeBase(
            collection_name=connection_info.get("collection_name", config.name),
            persist_directory=connection_info.get("persist_directory"),
            host=connection_info.get("host"),
            port=connection_info.get("port"),
            embedding_function=connection_info.get("embedding_function")
        )
    
    def get_knowledge_base(self, name: str) -> Optional[KnowledgeBase]:
        """获取知识库实例"""
        return self.knowledge_bases.get(name)
    
    def list_knowledge_bases(self) -> List[str]:
        """获取所有知识库名称"""
        return list(self.knowledge_bases.keys())
    
    def remove_knowledge_base(self, name: str) -> bool:
        """移除知识库"""
        if name in self.knowledge_bases:
            del self.knowledge_bases[name]
            if name in self.configs:
                del self.configs[name]
            logger.info(f"已移除知识库: {name}")
            return True
        return False
    
    # 统一的知识库操作接口
    def add_item(self, kb_name: str, item: KnowledgeItem) -> bool:
        """在指定知识库中添加知识项"""
        kb = self.get_knowledge_base(kb_name)
        if kb is None:
            logger.error(f"知识库 {kb_name} 不存在")
            return False
        return kb.add_item(item)
    
    def get_item(self, kb_name: str, item_id: str) -> Optional[KnowledgeItem]:
        """从指定知识库获取知识项"""
        kb = self.get_knowledge_base(kb_name)
        if kb is None:
            logger.error(f"知识库 {kb_name} 不存在")
            return None
        return kb.get_item(item_id)
    
    def search(self, kb_name: str, query: str, top_k: int = 10, 
               filter_dict: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """在指定知识库中搜索"""
        kb = self.get_knowledge_base(kb_name)
        if kb is None:
            logger.error(f"知识库 {kb_name} 不存在")
            return []
        return kb.search(query, top_k, filter_dict)
    
    def search_all(self, query: str, top_k: int = 10, 
                   filter_dict: Optional[Dict[str, Any]] = None,
                   kb_names: Optional[List[str]] = None) -> Dict[str, List[SearchResult]]:
        """
        在多个知识库中搜索
        
        Args:
            query: 搜索查询
            top_k: 每个知识库返回的最大结果数
            filter_dict: 过滤条件
            kb_names: 要搜索的知识库名称列表，如果为None则搜索所有知识库
            
        Returns:
            各个知识库的搜索结果
        """
        results: Dict[str, List[SearchResult]] = {}
        
        search_kbs = kb_names if kb_names else self.list_knowledge_bases()
        
        for kb_name in search_kbs:
            if kb_name in self.knowledge_bases:
                kb_results = self.search(kb_name, query, top_k, filter_dict)
                results[kb_name] = kb_results
        
        return results
    
    def update_item(self, kb_name: str, item_id: str, updates: Dict[str, Any]) -> bool:
        """更新指定知识库中的知识项"""
        kb = self.get_knowledge_base(kb_name)
        if kb is None:
            logger.error(f"知识库 {kb_name} 不存在")
            return False
        return kb.update_item(item_id, updates)
    
    def delete_item(self, kb_name: str, item_id: str) -> bool:
        """从指定知识库删除知识项"""
        kb = self.get_knowledge_base(kb_name)
        if kb is None:
            logger.error(f"知识库 {kb_name} 不存在")
            return False
        return kb.delete_item(item_id)
    
    def list_items(self, kb_name: str, category: Optional[str] = None, 
                   tags: Optional[List[str]] = None, limit: int = 100, 
                   offset: int = 0) -> List[KnowledgeItem]:
        """列出指定知识库中的知识项"""
        kb = self.get_knowledge_base(kb_name)
        if kb is None:
            logger.error(f"知识库 {kb_name} 不存在")
            return []
        return kb.list_items(category, tags, limit, offset)
    
    def get_stats(self, kb_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Args:
            kb_name: 知识库名称，如果为None则返回所有知识库的统计信息
            
        Returns:
            统计信息或所有知识库的统计信息
        """
        if kb_name:
            kb = self.get_knowledge_base(kb_name)
            if kb is None:
                logger.error(f"知识库 {kb_name} 不存在")
                return {}
            return kb.get_stats()
        else:
            # 返回所有知识库的统计信息
            all_stats: Dict[str, Any] = {}
            for name, kb in self.knowledge_bases.items():
                all_stats[name] = kb.get_stats()
            return all_stats
    
    def clear(self, kb_name: str) -> bool:
        """清空指定知识库"""
        kb = self.get_knowledge_base(kb_name)
        if kb is None:
            logger.error(f"知识库 {kb_name} 不存在")
            return False
        return kb.clear()
    
    def get_summary(self) -> Dict[str, Any]:
        """获取知识库管理器的摘要信息"""
        knowledge_bases_info: Dict[str, Any] = {}
        
        for name, config in self.configs.items():
            kb_info: Dict[str, Any] = {
                "type": config.type.value,
                "description": config.description,
                "enabled": config.enable
            }
            
            # 添加统计信息
            if name in self.knowledge_bases:
                stats = self.knowledge_bases[name].get_stats()
                kb_info["stats"] = stats
            
            knowledge_bases_info[name] = kb_info
        
        summary: Dict[str, Any] = {
            "total_knowledge_bases": len(self.knowledge_bases),
            "knowledge_bases": knowledge_bases_info
        }
        
        return summary 