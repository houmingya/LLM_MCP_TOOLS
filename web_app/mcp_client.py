"""
MCP Client 包装器
使用 FastMCP 的 Client 通过 HTTP 连接到 MCP Server
"""

import logging
import asyncio
from typing import Dict, Any, List
from fastmcp import Client

logger = logging.getLogger(__name__)


class MCPClientWrapper:
    """MCP 客户端包装器 - 通过 HTTP 与 MCP Server 通信"""
    
    def __init__(self, server_url: str = "http://localhost:8001/mcp"):
        """
        初始化 MCP 客户端
        
        Args:
            server_url: MCP Server 的 URL
        """
        self.server_url = server_url
        self._client = None
        self._tools_cache = None
    
    async def connect(self):
        """连接到 MCP Server"""
        if self._client is None:
            self._client = Client(self.server_url)
            await self._client.__aenter__()
            logger.info(f"已连接到 MCP Server: {self.server_url}")
    
    async def disconnect(self):
        """断开连接"""
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None
            logger.info("已断开 MCP Server 连接")
    
    async def get_tools_definition(self) -> List[Dict[str, Any]]:
        """
        从 MCP Server 获取工具定义
        
        Returns:
            OpenAI Function Calling 格式的工具定义列表
        """
        await self.connect()
        
        # 从 MCP Server 获取工具列表
        tools = await self._client.list_tools()
        
        # 转换为 OpenAI Function Calling 格式
        tool_definitions = []
        for tool in tools:
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or f"调用 {tool.name} 工具",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            
            # 如果工具有 inputSchema，使用它
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                schema = tool.inputSchema
                if isinstance(schema, dict):
                    tool_def["function"]["parameters"] = schema
            
            tool_definitions.append(tool_def)
        
        self._tools_cache = tool_definitions
        logger.info(f"从 MCP Server 加载了 {len(tool_definitions)} 个工具")
        return tool_definitions
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用 MCP Server 上的工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        await self.connect()
        
        try:
            # 通过 MCP 协议调用工具
            result = await self._client.call_tool(tool_name, arguments)
            
            # 提取结果内容
            if hasattr(result, 'content') and len(result.content) > 0:
                content = result.content[0]
                
                # 处理不同类型的返回内容
                if hasattr(content, 'text'):
                    # 文本内容，尝试解析为 JSON
                    import json
                    try:
                        return json.loads(content.text)
                    except:
                        return {"result": content.text}
                elif hasattr(content, 'data'):
                    return content.data
                else:
                    return {"result": str(content)}
            
            return {"result": "工具执行成功，但无返回内容"}
            
        except Exception as e:
            logger.error(f"调用工具 {tool_name} 失败: {e}")
            return {"error": str(e)}


# 全局 MCP 客户端实例
_mcp_client = None


def get_mcp_client() -> MCPClientWrapper:
    """获取全局 MCP 客户端实例"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClientWrapper()
    return _mcp_client
