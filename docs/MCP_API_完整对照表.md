# MCP API 完整对照表

## 当前项目使用的方法

### ✅ 已使用

| 功能 | 客户端方法 | HTTP API | 文件位置 |
|------|-----------|---------|---------|
| 获取工具列表 | `client.list_tools()` | `POST /mcp` `{"method": "tools/list"}` | `web_app/mcp_client.py:50` |
| 调用工具 | `client.call_tool(name, args)` | `POST /mcp` `{"method": "tools/call"}` | `web_app/mcp_client.py:83` |

### 💡 可以扩展使用的方法

#### 1. 资源管理
```python
from fastmcp import Client

client = Client("http://localhost:8001/mcp")
await client.__aenter__()

# 列出所有资源（如文档、指南等）
resources = await client.list_resources()

# 读取特定资源
content = await client.read_resource("system://prompts/tool-selection-guide")
```

**对应的 HTTP API：**
```python
import httpx

# 列出资源
response = httpx.post("http://localhost:8001/mcp", json={
    "jsonrpc": "2.0",
    "id": 1,
    "method": "resources/list",
    "params": {}
})

# 读取资源
response = httpx.post("http://localhost:8001/mcp", json={
    "jsonrpc": "2.0",
    "id": 2,
    "method": "resources/read",
    "params": {"uri": "system://prompts/tool-selection-guide"}
})
```

#### 2. 提示词管理
```python
# 列出提示词模板
prompts = await client.list_prompts()

# 获取格式化的提示词
prompt = await client.get_prompt("code-review", {"language": "python"})
```

**对应的 HTTP API：**
```python
# 列出提示词
response = httpx.post("http://localhost:8001/mcp", json={
    "jsonrpc": "2.0",
    "id": 3,
    "method": "prompts/list",
    "params": {}
})

# 获取提示词
response = httpx.post("http://localhost:8001/mcp", json={
    "jsonrpc": "2.0",
    "id": 4,
    "method": "prompts/get",
    "params": {
        "name": "code-review",
        "arguments": {"language": "python"}
    }
})
```

---

## MCP 协议完整 API 列表

### 📦 工具相关 (Tools)

| 方法 | 说明 | 客户端调用 | HTTP 请求 |
|------|------|-----------|----------|
| `tools/list` | 获取所有可用工具 | `await client.list_tools()` | `{"method": "tools/list", "params": {}}` |
| `tools/call` | 调用指定工具 | `await client.call_tool(name, args)` | `{"method": "tools/call", "params": {"name": "...", "arguments": {...}}}` |

### 📄 资源相关 (Resources)

| 方法 | 说明 | 客户端调用 | HTTP 请求 |
|------|------|-----------|----------|
| `resources/list` | 列出所有资源 | `await client.list_resources()` | `{"method": "resources/list", "params": {}}` |
| `resources/read` | 读取资源内容 | `await client.read_resource(uri)` | `{"method": "resources/read", "params": {"uri": "..."}}` |
| `resources/subscribe` | 订阅资源更新 | `await client.subscribe_resource(uri)` | `{"method": "resources/subscribe", "params": {"uri": "..."}}` |
| `resources/unsubscribe` | 取消订阅 | `await client.unsubscribe_resource(uri)` | `{"method": "resources/unsubscribe", "params": {"uri": "..."}}` |
| `notifications/resources/list_changed` | 资源列表变化通知 | - | 服务器推送 |
| `notifications/resources/updated` | 资源内容更新通知 | - | 服务器推送 |

### 💬 提示词相关 (Prompts)

| 方法 | 说明 | 客户端调用 | HTTP 请求 |
|------|------|-----------|----------|
| `prompts/list` | 列出所有提示词 | `await client.list_prompts()` | `{"method": "prompts/list", "params": {}}` |
| `prompts/get` | 获取提示词内容 | `await client.get_prompt(name, args)` | `{"method": "prompts/get", "params": {"name": "...", "arguments": {...}}}` |
| `notifications/prompts/list_changed` | 提示词列表变化通知 | - | 服务器推送 |

### 🤖 采样相关 (Sampling)

| 方法 | 说明 | 客户端调用 | HTTP 请求 |
|------|------|-----------|----------|
| `sampling/createMessage` | 请求 LLM 生成消息 | `await client.create_message(...)` | `{"method": "sampling/createMessage", "params": {...}}` |

### 🔌 连接管理

| 方法 | 说明 | 客户端调用 | HTTP 请求 |
|------|------|-----------|----------|
| `initialize` | 初始化连接 | 自动调用 | `{"method": "initialize", "params": {...}}` |
| `ping` | 心跳检测 | `await client.ping()` | `{"method": "ping", "params": {}}` |
| `notifications/initialized` | 初始化完成通知 | - | 客户端发送 |
| `notifications/cancelled` | 请求取消通知 | - | 双向 |
| `notifications/progress` | 进度更新通知 | - | 服务器推送 |

### 📊 日志相关

| 方法 | 说明 | 客户端调用 | HTTP 请求 |
|------|------|-----------|----------|
| `logging/setLevel` | 设置日志级别 | `await client.set_log_level(level)` | `{"method": "logging/setLevel", "params": {"level": "debug"}}` |
| `notifications/message` | 日志消息通知 | - | 服务器推送 |

---

## 完整 HTTP 请求格式

所有 MCP API 都使用 JSON-RPC 2.0 格式：

```python
import httpx

# 标准请求格式
request = {
    "jsonrpc": "2.0",          # 协议版本
    "id": 1,                   # 请求 ID（用于匹配响应）
    "method": "tools/list",    # 方法名
    "params": {}               # 参数（可选）
}

response = httpx.post("http://localhost:8001/mcp", json=request)
result = response.json()

# 响应格式
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {              # 成功时有 result
        "tools": [...]
    }
}

# 或错误响应
{
    "jsonrpc": "2.0",
    "id": 1,
    "error": {               # 失败时有 error
        "code": -32600,
        "message": "Invalid request"
    }
}
```

---

## 实际使用示例

### 示例 1: 使用客户端 SDK（推荐）

```python
from fastmcp import Client

async def main():
    # 创建客户端
    client = Client("http://localhost:8001/mcp")
    await client.__aenter__()
    
    try:
        # 1. 获取工具列表
        tools = await client.list_tools()
        print(f"可用工具: {[t.name for t in tools]}")
        
        # 2. 调用工具
        result = await client.call_tool("query_employee_by_id", {"employee_id": 1})
        print(f"结果: {result}")
        
        # 3. 获取资源
        resources = await client.list_resources()
        print(f"可用资源: {[r.uri for r in resources]}")
        
        # 4. 读取资源
        content = await client.read_resource("system://prompts/tool-selection-guide")
        print(f"资源内容: {content}")
        
    finally:
        await client.__aexit__(None, None, None)
```

### 示例 2: 直接使用 HTTP API

```python
import httpx
import json

async def call_mcp_api(method: str, params: dict = None):
    """通用 MCP API 调用函数"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/mcp",
            json=request
        )
        return response.json()

async def main():
    # 1. 获取工具列表
    result = await call_mcp_api("tools/list")
    print(result)
    
    # 2. 调用工具
    result = await call_mcp_api("tools/call", {
        "name": "query_employee_by_id",
        "arguments": {"employee_id": 1}
    })
    print(result)
    
    # 3. 读取资源
    result = await call_mcp_api("resources/read", {
        "uri": "system://prompts/tool-selection-guide"
    })
    print(result)
```

---

## 建议的扩展方向

### 1. 添加资源管理功能

在 `mcp_client.py` 中添加：

```python
async def list_resources(self) -> List[Dict[str, Any]]:
    """获取所有可用资源"""
    await self.connect()
    resources = await self._client.list_resources()
    return [{"uri": r.uri, "name": r.name, "description": r.description} 
            for r in resources]

async def read_resource(self, uri: str) -> str:
    """读取资源内容"""
    await self.connect()
    content = await self._client.read_resource(uri)
    return content
```

### 2. 添加提示词管理

```python
async def list_prompts(self) -> List[Dict[str, Any]]:
    """获取所有提示词模板"""
    await self.connect()
    prompts = await self._client.list_prompts()
    return [{"name": p.name, "description": p.description} 
            for p in prompts]

async def get_prompt(self, name: str, arguments: Dict[str, Any] = None) -> str:
    """获取格式化的提示词"""
    await self.connect()
    prompt = await self._client.get_prompt(name, arguments or {})
    return prompt
```

### 3. 添加健康检查

```python
async def ping(self) -> bool:
    """检查服务器连接"""
    try:
        await self.connect()
        await self._client.ping()
        return True
    except:
        return False
```

---

## 参考文档

- [MCP 官方规范](https://spec.modelcontextprotocol.io/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [JSON-RPC 2.0 规范](https://www.jsonrpc.org/specification)
