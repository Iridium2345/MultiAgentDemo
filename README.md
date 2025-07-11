# 多代理框架

这是一个用于管理多个AI代理的框架，支持API密钥管理、MCP工具、记忆库、知识库和代理模板管理。

## 🎯 核心功能

- **API密钥管理**: 安全管理多个AI服务的API密钥
- **MCP工具管理**: 集成和管理模型控制协议(MCP)工具
- **记忆库系统**: 代理对话历史和上下文记忆
- **知识库系统**: 基于向量数据库的语义搜索和知识管理
- **代理模板**: 灵活的代理配置和管理

## 🏗️ 架构概览

```
multi_agent_framework/
├── api_keys.py                 # API密钥管理
├── tool_manager.py             # MCP工具管理
├── memory_manager.py           # 记忆库管理
├── knowledge_base.py           # 知识库接口
├── knowledge_manager.py        # 知识库管理器
├── knowledge_bases/            # 知识库实现
│   ├── chroma_knowledge.py     # Chroma向量数据库
│   └── __init__.py
├── config/                     # 配置管理
│   ├── agent_config.py         # 代理配置
│   ├── memory_config.py        # 记忆配置
│   ├── knowledge_config.py     # 知识库配置
│   ├── tool_config.py          # 工具配置
│   └── loader.py               # 配置加载器
├── graph_agent.py              # 代理实现
├── chat_agent.py               # 聊天代理
└── simple_chat.py              # 简单聊天接口
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 基础依赖
pip install -e .

# 完整功能（包含知识库）
pip install chromadb>=0.4.0
```

### 2. 配置文件

```bash
# 创建配置目录
mkdir -p configs/agent configs/knowledge_bases configs/tools

# 复制示例配置
cp configs/agent/example.yaml configs/agent/my_agent.yaml
cp configs/knowledge_bases/chroma_example.yaml configs/knowledge_bases/my_kb.yaml
```

### 3. 基本使用

```python
from multi_agent_framework import GraphAgent

# 创建代理（自动加载配置的知识库）
agent = GraphAgent("configs/agent/my_agent.yaml")

# 开始对话
response = agent.chat("你好，请介绍一下Python编程", [])
print(response)
```

## 📚 核心组件详解

### 1. API密钥管理 (`api_keys.py`)
- **ApiKey**: 存储单个API密钥的信息
- **ApiKeys**: 从YAML文件加载和管理多个API密钥

```python
from multi_agent_framework import ApiKeys

# 加载API密钥
api_keys = ApiKeys("api_keys.yaml")

# 获取特定的API密钥
openai_key = api_keys.key_of("openai")
print(f"OpenAI Key: {openai_key.key}")
```

### 2. MCP工具管理 (`tool_manager.py`)
- **McpTool**: 代表一个MCP工具，包含描述、配置和启用状态
- **McpToolManager**: 管理多个MCP工具

```python
from multi_agent_framework import McpToolManager

# 加载MCP工具
tools = McpToolManager("mcp_tools.yaml")

# 获取启用的工具
enabled_tools = tools.get_enabled_tools()

# 启用/禁用工具
tools.enable_tool("search_tool")
tools.disable_tool("old_tool")
```

### 3. 记忆库管理 (`memory_manager.py`)
- **MemoryItem**: 存储单个记忆项，支持时间戳和元数据
- **MemoryManager**: 管理代理的记忆，支持读写操作

```python
from multi_agent_framework import MemoryManager, MemoryItem

# 创建记忆管理器
memory = MemoryManager("memory.json")

# 添加记忆
memory_item = MemoryItem("mem_1", "重要的对话内容", "conversation")
memory.add_memory(memory_item)

# 搜索记忆
results = memory.search_memories("对话", "conversation")

# 获取最近的记忆
recent = memory.get_recent_memories(10)
```

### 4. 知识库管理 (`knowledge_manager.py`) 🆕
- **KnowledgeItem**: 存储知识项，包含标题、内容、分类和标签
- **KnowledgeManager**: 管理知识库，支持多种向量数据库
- **KnowledgeBase**: 通用知识库接口，支持Chroma、FAISS、Pinecone等

```python
from multi_agent_framework import (
    KnowledgeManager, 
    KnowledgeItem, 
    KnowledgeBaseConfig
)

# 创建知识管理器
manager = KnowledgeManager()

# 创建知识库配置
config = KnowledgeBaseConfig(
    name="my_kb",
    type="chroma",
    enable=True,
    connection_info={
        "collection_name": "knowledge_base",
        "persist_directory": "./data/chroma_db"
    }
)

# 添加知识库
manager.add_knowledge_base("my_kb", config)

# 添加知识项
item = KnowledgeItem(
    id="python_intro",
    content="Python是一种高级编程语言...",
    title="Python介绍",
    category="programming",
    tags=["python", "编程"]
)
manager.add_item("my_kb", item)

# 语义搜索
results = manager.search("my_kb", "Python编程", top_k=5)
```

### 5. 代理管理 (`graph_agent.py`)
- **GraphAgent**: 基于图结构的代理，支持复杂的对话流程
- **AgentTemplate**: 代理模板，定义代理的配置
- **AgentManager**: 统一管理所有组件

```python
from multi_agent_framework import AgentManager

# 创建代理管理器
manager = AgentManager()

# 创建代理模板
template = manager.create_agent_template(
    name="助手代理",
    description="一个通用的助手代理",
    api_key_name="openai",
    instructions="你是一个友好的助手",
    memory_categories=["conversation", "user_info"],
    knowledge_categories=["general", "programming"],
    enabled_tools=["search_tool", "calculator"]
)

# 为代理添加记忆
memory_item = manager.add_agent_memory(
    template.id,
    "用户喜欢Python编程",
    "user_info"
)

# 获取代理的记忆
memories = manager.get_agent_memory(template.id)

# 获取代理的知识
knowledge = manager.get_agent_knowledge(template.id)

# 获取代理的工具
tools = manager.get_agent_tools(template.id)
```

## ⚙️ 配置文件格式

### API密钥配置 (`api_keys.yaml`)
```yaml
openai:
  type: "openai"
  key: "sk-your-openai-key"

anthropic:
  type: "anthropic"
  key: "your-anthropic-key"
```

### MCP工具配置 (`configs/tools/example.yaml`)
```yaml
name: "example_tool"
description: "示例工具"
schema:
  type: "function"
  properties:
    query:
      type: "string"
      description: "搜索查询"
enabled: true
config:
  api_url: "https://api.example.com"
```

### 代理配置 (`configs/agent/example.yaml`)
```yaml
description: "示例代理"
model_config:
  provider: "DeepSeek"
  model: "deepseek-chat"
  temperature: 0.5
  max_tokens: 4096
memory:
  type: "chroma"
  enabled: false
  url: "http://localhost:8000"
tools:
  - "example"
knowledge_bases:
  - "chroma_example"  # 引用知识库配置
system_prompt: "你是一个助手，可以使用工具和知识库来回答问题。"
```

### 知识库配置 (`configs/knowledge_bases/chroma_example.yaml`) 🆕
```yaml
name: "chroma_knowledge_base"
description: "基于Chroma的向量知识库"
type: "chroma"
enable: true
connection_info:
  collection_name: "knowledge_base"
  persist_directory: "./data/chroma_db"
  # 可选：连接到远程Chroma服务器
  # host: "localhost"
  # port: 8000
metadata:
  version: "1.0"
  created_by: "multi_agent_framework"
  purpose: "存储和检索知识库内容"
```

### 记忆库文件 (`memory.json`)
```json
{
  "memories": [
    {
      "id": "mem_1",
      "content": "用户询问关于Python的问题",
      "category": "conversation",
      "metadata": {
        "user_id": "user_123",
        "confidence": 0.8
      },
      "timestamp": "2024-01-15T10:30:00"
    }
  ],
  "last_updated": "2024-01-15T10:30:00"
}
```

## 🔧 知识库系统特性

### 支持的知识库类型
- ✅ **Chroma**: 开源向量数据库，支持本地和远程部署
- 🚧 **FAISS**: Facebook AI研究的向量搜索库（未来支持）
- 🚧 **Pinecone**: 托管向量数据库服务（未来支持）

### 核心功能
- **语义搜索**: 基于向量相似度的智能搜索
- **知识管理**: 添加、更新、删除知识项
- **分类和标签**: 灵活的知识组织方式
- **多知识库**: 支持同时管理多个知识库
- **配置驱动**: 通过配置文件管理知识库

### 数据模型
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

## 📖 使用示例

### 完整的代理对话示例
```python
from multi_agent_framework import GraphAgent

# 创建代理
agent = GraphAgent("configs/agent/example.yaml")

# 开始对话
messages = []
while True:
    user_input = input("用户: ")
    if user_input.lower() == 'quit':
        break
    
    response = agent.chat(user_input, messages)
    print(f"代理: {response}")
    
    # 更新消息历史
    messages.append({"role": "user", "content": user_input})
    messages.append({"role": "assistant", "content": response})
```

### 知识库集成示例
```python
from multi_agent_framework import KnowledgeManager, KnowledgeItem

# 创建知识管理器
manager = KnowledgeManager()

# 从配置文件加载知识库
from multi_agent_framework.config.loader import load_knowledge_config
config = load_knowledge_config("configs/knowledge_bases/chroma_example.yaml")
manager.add_knowledge_base("my_kb", config)

# 批量添加知识项
knowledge_items = [
    KnowledgeItem(
        id="python_basics",
        content="Python是一种解释型、高级编程语言...",
        title="Python基础",
        category="programming",
        tags=["python", "基础"]
    ),
    KnowledgeItem(
        id="ai_concepts",
        content="人工智能是计算机科学的一个分支...",
        title="AI概念",
        category="AI",
        tags=["AI", "机器学习"]
    )
]

for item in knowledge_items:
    manager.add_item("my_kb", item)

# 搜索相关知识
results = manager.search("my_kb", "Python编程入门", top_k=3)
for result in results:
    print(f"标题: {result.item.title}")
    print(f"相似度: {result.score:.3f}")
    print(f"内容: {result.item.content[:100]}...")
    print("-" * 50)
```

## 🎯 特性

- **模块化设计**: 每个组件都是独立的，可以单独使用
- **类型安全**: 使用Python类型提示确保代码质量
- **配置驱动**: 通过YAML配置文件管理所有组件
- **可扩展性**: 支持自定义工具、知识库和代理类型
- **异步支持**: 支持异步操作和并发处理
- **语义搜索**: 基于向量数据库的智能知识检索
- **多模态支持**: 支持文本、图像等多种数据类型

## 📁 项目结构

```
demo/
├── configs/                    # 配置文件目录
│   ├── agent/                  # 代理配置
│   │   ├── example.yaml
│   │   └── ...
│   ├── knowledge_bases/        # 知识库配置
│   │   ├── chroma_example.yaml
│   │   └── ...
│   ├── tools/                  # 工具配置
│   │   ├── example.yaml
│   │   └── ...
│   └── db/                     # 数据库配置
├── multi_agent_framework/      # 核心框架
│   ├── knowledge_bases/        # 知识库实现
│   ├── config/                 # 配置管理
│   └── ...
├── examples/                   # 示例代码
├── tests/                      # 测试文件
├── docs/                       # 文档
│   └── knowledge_base_guide.md # 知识库详细指南
└── README.md                   # 本文档
```

## 📚 文档

- **[知识库系统使用指南](docs/knowledge_base_guide.md)**: 详细的知识库使用说明
- **[配置文件说明](configs/README.md)**: 各种配置文件的详细说明
- **[API文档](docs/api.md)**: 完整的API参考文档

## 🤝 贡献

欢迎提交问题和拉取请求。在提交之前，请确保：

1. 代码符合Python风格指南
2. 添加适当的类型提示
3. 包含必要的测试
4. 更新相关文档

## 📄 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件。