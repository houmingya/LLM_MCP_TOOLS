"""
统一启动入口
支持两种运行模式：
1. 解耦模式（推荐）：MCP Server 和 Web App 分离部署
2. 集成模式：仅启动 Web App（需要手动启动 MCP Server）
"""

import sys
import argparse
import subprocess
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_decoupled():
    """运行解耦模式：同时启动 MCP Server 和 Web App"""
    logger.info("="*70)
    logger.info("启动模式：解耦架构（MCP Server + Web App）")
    logger.info("="*70)
    
    try:
        # 调用 run_decoupled.py
        subprocess.run([sys.executable, "run_decoupled.py"], check=True)
    except KeyboardInterrupt:
        logger.info("\n正在停止所有服务...")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        sys.exit(1)


def run_webapp_only():
    """仅运行 Web App（需要 MCP Server 已启动）"""
    logger.info("="*70)
    logger.info("启动模式：Web App Only")
    logger.info("提示：请确保 MCP Server 已在 http://localhost:8001 运行")
    logger.info("     如需启动 MCP Server，请运行: python run_mcp_server.py")
    logger.info("="*70)
    
    try:
        from web_app.main import run_web_app
        run_web_app()
    except KeyboardInterrupt:
        logger.info("\n正在停止 Web App...")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        logger.exception(e)
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='FastMCP 智能工具调度系统')
    parser.add_argument(
        '--mode',
        choices=['decoupled', 'webapp'],
        default='decoupled',
        help='运行模式: decoupled=完整系统, webapp=仅Web应用'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'decoupled':
        run_decoupled()
    else:
        run_webapp_only()


if __name__ == "__main__":
    main()
