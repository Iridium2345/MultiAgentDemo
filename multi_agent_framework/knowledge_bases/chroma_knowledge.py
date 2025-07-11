"""
基于 Chroma 的知识库实现
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None
    Settings = None

from ..knowledge_base import KnowledgeBase, KnowledgeItem, SearchResult

logger = logging.getLogger(__name__)

class ChromaKnowledgeBase(KnowledgeBase):
    """基于 Chroma 的知识库实现"""
    
    def __init__(self, collection_name: str = "knowledge_base", 
                 persist_directory: Optional[str] = None,
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 embedding_function: Optional[Any] = None):
        """
        初始化 Chroma 知识库
        
        Args:
            collection_name: 集合名称
            persist_directory: 持久化目录路径
            host: Chroma 服务器地址
            port: Chroma 服务器端口
            embedding_function: 嵌入函数
        """
        if chromadb is None:
            raise ImportError("ChromaDB 未安装，请运行: pip install chromadb")
        
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.host = host
        self.port = port
        
        # 初始化 Chroma 客户端
        if host and port:
            # 连接到远程 Chroma 服务器
            self.client = chromadb.HttpClient(host=host, port=port)
        else:
            # 使用本地持久化客户端
            settings = Settings() if Settings else None
            if persist_directory and settings:
                settings.persist_directory = persist_directory
            self.client = chromadb.PersistentClient(settings=settings)
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
        
        logger.info(f"Chroma 知识库已初始化: {collection_name}")
    
    def add_item(self, item: KnowledgeItem) -> bool:
        """添加知识项到 Chroma 知识库"""
        try:
            # 准备元数据
            metadata = {
                "title": item.title or "",
                "category": item.category or "",
                "tags": ",".join(item.tags) if item.tags else "",
                "created_at": item.created_at.isoformat() if item.created_at else datetime.now().isoformat(),
                **(item.metadata or {})
            }
            
            # 添加到集合
            self.collection.add(
                documents=[item.content],
                metadatas=[metadata],
                ids=[item.id]
            )
            
            logger.info(f"成功添加知识项: {item.id}")
            return True
            
        except Exception as e:
            logger.error(f"添加知识项失败 {item.id}: {e}")
            return False
    
    def get_item(self, item_id: str) -> Optional[KnowledgeItem]:
        """根据 ID 获取知识项"""
        try:
            result = self.collection.get(ids=[item_id])
            
            if not result["ids"]:
                return None
            
            # 构造知识项
            doc = result["documents"][0]
            metadata = result["metadatas"][0]
            
            # 解析标签
            tags = []
            if metadata.get("tags"):
                tags = [tag.strip() for tag in metadata["tags"].split(",") if tag.strip()]
            
            # 解析创建时间
            created_at = None
            if metadata.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(metadata["created_at"])
                except ValueError:
                    pass
            
            # 分离标准字段和自定义元数据
            standard_fields = {"title", "category", "tags", "created_at"}
            custom_metadata = {k: v for k, v in metadata.items() if k not in standard_fields}
            
            return KnowledgeItem(
                id=item_id,
                content=doc,
                title=metadata.get("title") or None,
                category=metadata.get("category") or None,
                tags=tags,
                metadata=custom_metadata,
                created_at=created_at
            )
            
        except Exception as e:
            logger.error(f"获取知识项失败 {item_id}: {e}")
            return None
    
    def search(self, query: str, top_k: int = 10, filter_dict: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """在 Chroma 知识库中进行语义搜索"""
        try:
            # 构建过滤条件
            where_clause = {}
            if filter_dict:
                where_clause = filter_dict.copy()
            
            # 执行搜索
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_clause if where_clause else None
            )
            
            search_results = []
            
            if results["ids"][0]:  # 有结果
                for idx, (doc_id, doc, metadata, distance) in enumerate(zip(
                    results["ids"][0],
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    # 构造知识项
                    tags = []
                    if metadata.get("tags"):
                        tags = [tag.strip() for tag in metadata["tags"].split(",") if tag.strip()]
                    
                    created_at = None
                    if metadata.get("created_at"):
                        try:
                            created_at = datetime.fromisoformat(metadata["created_at"])
                        except ValueError:
                            pass
                    
                    standard_fields = {"title", "category", "tags", "created_at"}
                    custom_metadata = {k: v for k, v in metadata.items() if k not in standard_fields}
                    
                    item = KnowledgeItem(
                        id=doc_id,
                        content=doc,
                        title=metadata.get("title") or None,
                        category=metadata.get("category") or None,
                        tags=tags,
                        metadata=custom_metadata,
                        created_at=created_at
                    )
                    
                    # 计算相似度分数（距离越小，相似度越高）
                    score = 1.0 - distance if distance is not None else 0.0
                    
                    search_results.append(SearchResult(
                        item=item,
                        score=score,
                        rank=idx + 1
                    ))
            
            logger.info(f"搜索完成，找到 {len(search_results)} 个结果")
            return search_results
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def update_item(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """更新知识项"""
        try:
            # 首先获取现有项
            existing_item = self.get_item(item_id)
            if not existing_item:
                logger.warning(f"要更新的知识项不存在: {item_id}")
                return False
            
            # 应用更新
            updated_content = updates.get("content", existing_item.content)
            updated_title = updates.get("title", existing_item.title)
            updated_category = updates.get("category", existing_item.category)
            updated_tags = updates.get("tags", existing_item.tags)
            updated_metadata = existing_item.metadata.copy()
            updated_metadata.update(updates.get("metadata", {}))
            
            # 创建更新后的知识项
            updated_item = KnowledgeItem(
                id=item_id,
                content=updated_content,
                title=updated_title,
                category=updated_category,
                tags=updated_tags,
                metadata=updated_metadata,
                created_at=existing_item.created_at
            )
            
            # 删除旧项并添加新项
            self.delete_item(item_id)
            return self.add_item(updated_item)
            
        except Exception as e:
            logger.error(f"更新知识项失败 {item_id}: {e}")
            return False
    
    def delete_item(self, item_id: str) -> bool:
        """删除知识项"""
        try:
            self.collection.delete(ids=[item_id])
            logger.info(f"成功删除知识项: {item_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除知识项失败 {item_id}: {e}")
            return False
    
    def list_items(self, category: Optional[str] = None, tags: Optional[List[str]] = None, 
                   limit: int = 100, offset: int = 0) -> List[KnowledgeItem]:
        """列出知识项"""
        try:
            # 构建过滤条件
            where_clause = {}
            if category:
                where_clause["category"] = category
            
            # 获取所有匹配的项
            result = self.collection.get(
                where=where_clause if where_clause else None,
                limit=limit,
                offset=offset
            )
            
            items = []
            for doc_id, doc, metadata in zip(result["ids"], result["documents"], result["metadatas"]):
                # 解析标签
                item_tags = []
                if metadata.get("tags"):
                    item_tags = [tag.strip() for tag in metadata["tags"].split(",") if tag.strip()]
                
                # 如果指定了标签过滤，检查是否匹配
                if tags and not any(tag in item_tags for tag in tags):
                    continue
                
                # 解析创建时间
                created_at = None
                if metadata.get("created_at"):
                    try:
                        created_at = datetime.fromisoformat(metadata["created_at"])
                    except ValueError:
                        pass
                
                # 分离标准字段和自定义元数据
                standard_fields = {"title", "category", "tags", "created_at"}
                custom_metadata = {k: v for k, v in metadata.items() if k not in standard_fields}
                
                items.append(KnowledgeItem(
                    id=doc_id,
                    content=doc,
                    title=metadata.get("title") or None,
                    category=metadata.get("category") or None,
                    tags=item_tags,
                    metadata=custom_metadata,
                    created_at=created_at
                ))
            
            logger.info(f"列出 {len(items)} 个知识项")
            return items
            
        except Exception as e:
            logger.error(f"列出知识项失败: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        try:
            # 获取集合信息
            count = self.collection.count()
            
            # 获取一些样本数据来分析
            sample_result = self.collection.get(limit=min(100, count))
            
            categories = set()
            tags = set()
            
            for metadata in sample_result["metadatas"]:
                if metadata.get("category"):
                    categories.add(metadata["category"])
                if metadata.get("tags"):
                    item_tags = [tag.strip() for tag in metadata["tags"].split(",") if tag.strip()]
                    tags.update(item_tags)
            
            return {
                "total_items": count,
                "categories": list(categories),
                "tags": list(tags),
                "collection_name": self.collection_name
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {"total_items": 0, "categories": [], "tags": []}
    
    def clear(self) -> bool:
        """清空知识库"""
        try:
            # 获取所有文档 ID
            all_ids = self.collection.get()["ids"]
            
            if all_ids:
                # 删除所有文档
                self.collection.delete(ids=all_ids)
            
            logger.info("知识库已清空")
            return True
            
        except Exception as e:
            logger.error(f"清空知识库失败: {e}")
            return False 