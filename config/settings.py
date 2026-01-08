"""
系统配置文件
包含大模型、数据库、向量数据库等配置信息
支持从环境变量读取敏感配置
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 上传文件目录
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 向量数据库目录
CHROMA_DIR = BASE_DIR / "chroma_db"
CHROMA_DIR.mkdir(exist_ok=True)

# 知识图谱持久化目录
KNOWLEDGE_GRAPH_DIR = BASE_DIR / "knowledge_graph_data"
KNOWLEDGE_GRAPH_DIR.mkdir(exist_ok=True)


# ========================
# 大模型配置
# ========================
class LLMConfig:
    """大模型配置类 - 从环境变量读取"""
    
    # API配置（从环境变量读取，无默认值以确保安全）
    API_KEY: str = os.getenv("LLM_API_KEY", "")
    API_BASE: str = os.getenv("LLM_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "qwen-plus")
    
    # Embedding模型配置
    EMBEDDING_MODEL: str = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-v3")

    # 模型参数
    TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "api_key": cls.API_KEY,
            "api_base": cls.API_BASE,
            "model_name": cls.MODEL_NAME,
            "temperature": cls.TEMPERATURE,
            "max_tokens": cls.MAX_TOKENS,
        }


# ========================
# MySQL数据库配置
# ========================
class DatabaseConfig:
    """MySQL数据库配置类 - 从环境变量读取"""
    
    HOST: str = os.getenv("DB_HOST", "localhost")
    PORT: int = int(os.getenv("DB_PORT", "3306"))
    USER: str = os.getenv("DB_USER", "root")
    PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DATABASE: str = os.getenv("DB_DATABASE", "test_db")
    CHARSET: str = os.getenv("DB_CHARSET", "utf8mb4")
    
    # 连接池配置
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    POOL_RECYCLE: int = 3600
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "user": cls.USER,
            "password": cls.PASSWORD,
            "database": cls.DATABASE,
            "charset": cls.CHARSET,
        }
    
    @classmethod
    def get_connection_string(cls) -> str:
        """获取数据库连接字符串"""
        return f"mysql+pymysql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.DATABASE}?charset={cls.CHARSET}"


# ========================
# 向量数据库配置
# ========================
class VectorDBConfig:
    """向量数据库配置类"""
    
    # Chroma配置
    PERSIST_DIRECTORY: Path = CHROMA_DIR
    COLLECTION_NAME: str = "documents"
    
    # 向量检索配置
    TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7


# ========================
# Web应用配置
# ========================
class WebConfig:
    """Web应用配置类 - 从环境变量读取"""
    
    # FastAPI配置
    HOST: str = os.getenv("WEB_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("WEB_PORT", "8000"))
    RELOAD: bool = os.getenv("WEB_RELOAD", "true").lower() == "true"
    
    # CORS配置
    ALLOW_ORIGINS: list = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list = ["*"]
    ALLOW_HEADERS: list = ["*"]
    ALLOW_HEADERS: list = ["*"]
    
    # WebSocket配置
    WS_HEARTBEAT_INTERVAL: int = 30  # 心跳间隔（秒）


# ========================
# MCP服务器配置
# ========================
class MCPConfig:
    """MCP服务器配置类 - 从环境变量读取"""
    
    HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("MCP_PORT", "8001"))
    
    SERVER_NAME: str = "intelligent-tool-dispatcher"
    SERVER_VERSION: str = "1.0.0"
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


# ========================
# 工具配置
# ========================
class ToolConfig:
    """工具配置类 - 从环境变量读取"""
    
    # API工具配置
    REQUEST_TIMEOUT: int = 30
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # 天气API配置（可选）
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5/weather"
    
    # 计算工具配置
    MAX_CALCULATION_LENGTH: int = 1000  # 最大计算表达式长度


# ========================
# 导出配置
# ========================
__all__ = [
    "BASE_DIR",
    "UPLOAD_DIR",
    "CHROMA_DIR",
    "KNOWLEDGE_GRAPH_DIR",
    "LLMConfig",
    "DatabaseConfig",
    "VectorDBConfig",
    "WebConfig",
    "MCPConfig",
    "ToolConfig",
]
