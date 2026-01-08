"""
独立运行 MCP Server
使用 HTTP Transport，监听 8001 端口
"""

import logging
from mcp_server.server import mcp
from config.settings import MCPConfig

# 配置日志
logging.basicConfig(
    level=getattr(logging, MCPConfig.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("启动 MCP Server (HTTP Transport)")
    logger.info("=" * 60)
    logger.info(f"服务名称: {MCPConfig.SERVER_NAME}")
    logger.info(f"版本: {MCPConfig.SERVER_VERSION}")
    logger.info(f"监听地址: http://0.0.0.0:8001/mcp")
    logger.info("=" * 60)
    
    # 使用 HTTP Transport 运行 MCP Server
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8001,
        path="/mcp"
    )
