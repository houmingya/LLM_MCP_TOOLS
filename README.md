# FastMCP 2.0 智能工具调度系统

基于 FastMCP 2.0 的学习项目，采用 **MCP 解耦架构**，Server 和 Client 完全分离。

## ✨ 核心特性

- **🔧 6类工具**：数据库、知识库、计算、时间、API（共19个函数）
- **🧠 智能调度**：大模型自主选择和调用工具（Function Calling）
- **💬 多轮对话**：上下文理解 + 会话管理（限制20轮）
- **🌐 Web界面**：实时聊天 + Markdown 渲染
- **� 解耦架构**：MCP Server (8001) ←→ Web App (8000)

## 🏗️ 技术栈

```
FastMCP 2.0 (HTTP)  +  FastAPI (WebSocket)  +  通义千问 Qwen  +  MySQL/ChromaDB
```

## 📁 项目结构

```
MCP_test/
├── run.py                    # ⭐ 统一启动入口
├── run_decoupled.py         # 同时启动两服务
├── run_mcp_server.py        # 单独启动 MCP Server
│
├── config/
│   └── settings.py          # 配置中心（数据库、LLM、端口等）
│
├── mcp_server/              # MCP Server (port 8001)
│   ├── server.py            # 🎯 工具注册 @mcp.tool()
│   └── tools/               # 工具实现（6个模块）
│       ├── database_tools.py
│       ├── knowledge_tools.py
│       ├── calculation_tools.py
│       ├── time_tools.py
│       └── api_tools.py
│
└── web_app/                 # Web App (port 8000)
    ├── main.py              # 🎯 FastAPI + WebSocket + LLM
    ├── mcp_client.py        # 🎯 MCP Client（HTTP通信）
    └── static/index.html    # 前端界面
```

## 🎯 MCP 解耦架构

### 架构图
```
用户浏览器 (localhost:8000)
    ↓ WebSocket
Web App (FastAPI)
    ↓ HTTP (MCP Protocol)
MCP Server (FastMCP)
    ↓
工具函数 → 数据库/API
```

### 核心优势
✅ **添加工具超简单**：只需在 `mcp_server/server.py` 用 `@mcp.tool()` 注册  
✅ **自动工具发现**：Web App 通过 MCP Client 自动获取工具列表  
✅ **标准协议**：使用 MCP over HTTP (JSON-RPC)  
✅ **独立部署**：两个服务可分离部署和扩展

## 🚀 快速开始

### 1. 安装依赖
```bash
conda create -n mcp-demo python=3.10 -y
conda activate mcp-demo
pip install -r requirements.txt
```

### 2. 配置
编辑 `config/settings.py`：
- `LLMConfig` - 大模型 API Key
- `DatabaseConfig` - MySQL 连接信息

### 3. 启动

**方式一：一键启动（推荐）**
```bash
python run.py
# → MCP Server: http://localhost:8001/mcp
# → Web App: http://localhost:8000
```

**方式二：分别启动（调试用）**
```bash
# 终端1
python run_mcp_server.py

# 终端2
python run.py --mode webapp
```

### 4. 访问
浏览器打开：**http://localhost:8000**

### 常见问题
- **ChromaDB 错误**：删除 `chroma_db` 目录后重启
- **端口占用**：修改 `config/settings.py` 中的端口配置

## 📦 工具列表（19个）

| 类别 | 工具 | 说明 |
|-----|------|------|
| 📊 **数据库** | query_employees, query_departments 等 | 员工/部门查询统计 (6个) |
| 📚 **知识库** | search_documents, upload_document | 文档向量搜索 (3个) |
| 🧮 **计算** | calculate, statistics_analysis | 数学计算/统计 (3个) |
| ⏰ **时间** | get_current_time, date_calculation | 时间日期操作 (4个) |
| 🌐 **API** | http_request, get_weather | HTTP请求/天气 (3个) |

## 💡 使用示例

```
👤 查询销售部有多少员工
🤖 [调用 query_employees_by_department] 销售部共有 15 名员工

👤 帮我计算 (123 + 456) * 2
🤖 [调用 calculate] 计算结果：1158

👤 上传的文档里有什么内容？
🤖 [调用 search_documents] 在"员工手册"中找到关于请假制度的说明...
```

## 🔧 添加新工具

只需在 `mcp_server/server.py` 中添加：

```python
@mcp.tool()
def my_new_tool(param: str) -> Dict:
    """新工具描述"""
    # 实现逻辑
    return {"result": "success"}
```

重启 MCP Server，Web App 会**自动识别**！✨  
无需修改 `main.py`、工具列表或前端代码。

## 📚 核心文件说明

| 文件 | 作用 |
|-----|------|
| `mcp_server/server.py` | 🎯 工具注册中心（@mcp.tool()） |
| `web_app/main.py` | 🎯 FastAPI应用 + LLM集成 |
| `web_app/mcp_client.py` | 🎯 MCP Client（HTTP通信） |
| `config/settings.py` | 配置中心（数据库、LLM、端口） |

## 参考资源

- [FastMCP 官方文档](https://gofastmcp.com/)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [ChromaDB 文档](https://docs.trychroma.com/)

---

**Happy Learning! 🎓**
