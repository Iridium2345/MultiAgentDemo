# 多代理框架

这是一个用于管理多个AI代理的框架，支持API密钥管理、MCP工具、记忆库、知识库和代理模板管理。

## 核心组件

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

### 2. MCP工具管理 (`mcp_tools.py`)
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

### 4. 知识库管理 (`knowledge_manager.py`)
- **KnowledgeItem**: 存储知识项，包含标题、内容、分类和标签
- **KnowledgeManager**: 管理知识库，只读操作

```python
from multi_agent_framework import KnowledgeManager

# 创建知识管理器
knowledge = KnowledgeManager("knowledge.json")

# 搜索知识
results = knowledge.search_knowledge("Python编程", "programming")

# 按分类获取知识
python_knowledge = knowledge.get_by_category("python")

# 按标签获取知识
tutorial_knowledge = knowledge.get_by_tag("tutorial")
```

### 5. 代理管理 (`agent_manager.py`)
- **AgentTemplate**: 代理模板，定义代理的配置
- **AgentTemplates**: 管理多个代理模板
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

## 配置文件格式

### API密钥配置 (`api_keys.yaml`)
```yaml
openai:
  type: "openai"
  key: "sk-your-openai-key"

anthropic:
  type: "anthropic"
  key: "your-anthropic-key"
```

### MCP工具配置 (`mcp_tools.yaml`)
```yaml
search_tool:
  description: "网络搜索工具"
  schema:
    type: "function"
    properties:
      query:
        type: "string"
        description: "搜索查询"
  enabled: true
  config:
    api_url: "https://api.search.com"

calculator:
  description: "计算器工具"
  schema:
    type: "function"
    properties:
      expression:
        type: "string"
        description: "数学表达式"
  enabled: true
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

### 知识库文件 (`knowledge.json`)
```json
{
  "knowledge_items": [
    {
      "id": "k1",
      "title": "Python基础语法",
      "content": "Python是一种解释型、面向对象的编程语言...",
      "category": "programming",
      "tags": ["python", "基础", "语法"],
      "metadata": {
        "difficulty": "beginner",
        "source": "官方文档"
      },
      "created_at": "2024-01-15T10:00:00"
    }
  ]
}
```

## 特性

- **模块化设计**: 每个组件都是独立的，可以单独使用
- **类型安全**: 使用Python类型提示确保代码质量
- **文件持久化**: 支持JSON和YAML格式的配置文件
- **错误处理**: 完善的异常处理机制
- **搜索功能**: 支持记忆和知识的全文搜索
- **分类管理**: 支持按分类组织记忆和知识
- **工具管理**: 动态启用/禁用MCP工具
- **代理模板**: 可重用的代理配置模板

## 安装依赖

```bash
pip install pyyaml
```

## 使用示例

完整的使用示例请参考 `__main__.py` 文件。

## 项目结构

```
multi_agent_framework/
├── __init__.py          # 导出所有公共类
├── __main__.py          # 主程序入口
├── api_keys.py          # API密钥管理
├── mcp_tools.py         # MCP工具管理
├── memory_manager.py    # 记忆库管理
├── knowledge_manager.py # 知识库管理
└── agent_manager.py     # 代理管理
```