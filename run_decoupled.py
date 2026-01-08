"""
启动脚本（解耦架构）
同时启动 MCP Server 和 Web App，实现完全分离
"""

import subprocess
import sys
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 70)
    logger.info("启动智能工具调度系统（MCP 解耦架构）")
    logger.info("=" * 70)
    logger.info("架构说明：")
    logger.info("  - MCP Server (HTTP): http://localhost:8001/mcp")
    logger.info("  - Web App:           http://localhost:8000")
    logger.info("  - 通信协议:          MCP via HTTP")
    logger.info("=" * 70)
    
    processes = []
    
    try:
        # 1. 启动 MCP Server
        logger.info("\n[1/2] 启动 MCP Server...")
        mcp_server = subprocess.Popen(
            [sys.executable, "run_mcp_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1
        )
        processes.append(("MCP Server", mcp_server))
        logger.info("✓ MCP Server 已启动 (PID: {})".format(mcp_server.pid))
        
        # 等待 MCP Server 启动
        time.sleep(3)
        
        # 2. 启动 Web App
        logger.info("\n[2/2] 启动 Web App...")
        web_app = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "web_app.main:app", 
             "--host", "0.0.0.0", "--port", "8000", "--reload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1
        )
        processes.append(("Web App", web_app))
        logger.info("✓ Web App 已启动 (PID: {})".format(web_app.pid))
        
        logger.info("\n" + "=" * 70)
        logger.info("🎉 系统启动完成！")
        logger.info("=" * 70)
        logger.info("访问地址：http://localhost:8000")
        logger.info("按 Ctrl+C 停止所有服务")
        logger.info("=" * 70 + "\n")
        
        # 保持运行并显示日志
        while True:
            for name, process in processes:
                line = process.stdout.readline()
                if line:
                    print(f"[{name}] {line.rstrip()}")
                    
            # 检查进程是否还在运行
            for name, process in processes:
                if process.poll() is not None:
                    logger.error(f"{name} 进程已退出 (返回码: {process.returncode})")
                    raise Exception(f"{name} 异常退出")
                    
    except KeyboardInterrupt:
        logger.info("\n\n收到停止信号，正在关闭所有服务...")
    except Exception as e:
        logger.error(f"\n系统错误: {e}")
    finally:
        # 停止所有进程
        for name, process in processes:
            if process.poll() is None:
                logger.info(f"停止 {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        logger.info("所有服务已停止")


if __name__ == "__main__":
    main()
