# 知识库系统使用指南

## 概述

本多代理框架提供了一个通用的知识库系统，支持多种向量数据库后端。当前支持 Chroma 向量数据库，未来可以扩展支持 FAISS、Pinecone 等其他知识库类型。

## 核心组件

### 1. KnowledgeBase (抽象基类)
定义了所有知识库实现必须支持的基本操作：
- `add_item()`: 添加知识项
- `get_item()`: 获取知识项
- `search()`: 语义搜索
- `update_item()`: 更新知识项
- `delete_item()`: 删除知识项
- `list_items()`: 列出知识项
- `get_stats()`: 获取统计信息
- `clear()`: 清空知识库

### 2. KnowledgeItem (数据模型)
知识项的数据结构：
```python
@dataclass
class KnowledgeItem:
    id: str                                    # 唯一标识符
    content: str                               # 知识内容
    title: Optional[str] = None                # 标题
    category: Optional[str] = None             # 分类
    tags: Optional[List[str]] = None           # 标签
    metadata: Optional[Dict[str, Any]] = None  # 元数据
    created_at: Optional[datetime] = None      # 创建时间
    embedding: Optional[List[float]] = None    # 嵌入向量
```

### 3. KnowledgeManager (管理器)
统一管理多个知识库实例，提供：
- 知识库的创建和管理
- 统一的操作接口
- 多知识库搜索支持

## 快速开始

### 1. 安装依赖
```bash
pip install chromadb>=0.4.0
```

### 2. 创建知识库配置
```yaml
# configs/knowledge_bases/chroma_example.yaml
name: "my_knowledge_base"
description: "我的知识库"
type: "chroma"
enable: true
connection_info:
  collection_name: "knowledge_base"
  persist_directory: "./data/chroma_db"
  # 可选：连接到远程 Chroma 服务器
  # host: "localhost"
  # port: 8000
```

### 3. 基本使用示例
```python
from multi_agent_framework import (
    KnowledgeManager,
    KnowledgeBaseConfig,
    KnowledgeItem
)

# 创建管理器
manager = KnowledgeManager()

# 创建配置
config = KnowledgeBaseConfig(
    name="demo_kb",
    description="演示知识库",
    type="chroma",
    enable=True,
    connection_info={
        "collection_name": "demo",
        "persist_directory": "./data/chroma"
    }
)

# 添加知识库
manager.add_knowledge_base("demo", config)

# 创建知识项
item = KnowledgeItem(
    id="python_intro",
    content="Python是一种高级编程语言...",
    title="Python介绍",
    category="programming",
    tags=["python", "编程"]
)

# 添加知识项
manager.add_item("demo", item)

# 搜索知识项
results = manager.search("demo", "Python编程", top_k=5)
for result in results:
    print(f"{result.item.title}: {result.score:.3f}")
```

## 高级功能

### 1. 多知识库搜索
```python
# 在所有知识库中搜索
all_results = manager.search_all("Python", top_k=3)

# 在指定知识库中搜索
specific_results = manager.search_all(
    "Python", 
    top_k=3, 
    kb_names=["kb1", "kb2"]
)
```

### 2. 条件过滤
```python
# 按分类过滤
results = manager.search(
    "demo", 
    "编程", 
    filter_dict={"category": "programming"}
)

# 按标签列出
items = manager.list_items("demo", tags=["python"])
```

### 3. 知识项管理
```python
# 更新知识项
updates = {
    "content": "新的内容...",
    "tags": ["python", "高级"]
}
manager.update_item("demo", "python_intro", updates)

# 删除知识项
manager.delete_item("demo", "python_intro")
```

### 4. 统计信息
```python
# 获取单个知识库统计
stats = manager.get_stats("demo")
print(f"知识项数: {stats['total_items']}")

# 获取所有知识库统计
all_stats = manager.get_stats()

# 获取管理器摘要
summary = manager.get_summary()
```

## 扩展支持

### 添加新的知识库类型
1. 继承 `KnowledgeBase` 抽象基类
2. 实现所有必需的方法
3. 在 `KnowledgeType` 枚举中添加新类型
4. 在 `KnowledgeManager` 中添加创建逻辑

示例：
```python
class MyKnowledgeBase(KnowledgeBase):
    def add_item(self, item: KnowledgeItem) -> bool:
        # 实现添加逻辑
        pass
    
    def search(self, query: str, top_k: int = 10, 
               filter_dict: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        # 实现搜索逻辑
        pass
    
    # ... 实现其他方法
```

## 配置选项

### Chroma 配置参数
- `collection_name`: 集合名称
- `persist_directory`: 持久化目录
- `host`: Chroma 服务器地址（可选）
- `port`: Chroma 服务器端口（可选）
- `embedding_function`: 自定义嵌入函数（可选）

### 通用配置参数
- `name`: 知识库名称
- `description`: 知识库描述
- `type`: 知识库类型（"chroma", "faiss", "pinecone" 等）
- `enable`: 是否启用
- `connection_info`: 连接信息
- `metadata`: 元数据

## 最佳实践

1. **合理分类**: 使用 `category` 字段对知识进行分类
2. **标签管理**: 使用 `tags` 字段添加多个标签便于检索
3. **元数据利用**: 使用 `metadata` 字段存储额外信息
4. **定期维护**: 定期清理和更新知识库内容
5. **性能优化**: 根据使用场景选择合适的 `top_k` 值

## 运行示例

```bash
# 运行知识库示例
python examples/knowledge_base_example.py
```

这个示例展示了知识库系统的完整使用流程，包括创建、添加、搜索、更新和统计等操作。 