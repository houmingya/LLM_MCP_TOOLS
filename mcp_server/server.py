import logging
from typing import Any, Dict
from collections import defaultdict
from fastmcp import FastMCP
from config.settings import MCPConfig
from mcp_server.tools.database_tools import db_tools
from mcp_server.tools.knowledge_tools import knowledge_tools
from mcp_server.tools.knowledge_graph_tools import knowledge_graph_tools
from mcp_server.tools.calculation_tools import calc_tools
from mcp_server.tools.time_tools import time_tools
from mcp_server.tools.api_tools import api_tools
from mcp_server.prompts import TOOL_SELECTION_GUIDE, INTERACTION_EXAMPLES

# 配置日志
logging.basicConfig(
    level=getattr(logging, MCPConfig.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastMCP实例
mcp = FastMCP(
    name=MCPConfig.SERVER_NAME,
    version=MCPConfig.SERVER_VERSION
)


# ========================
# 资源 - 系统提示词和指南
# ========================

@mcp.resource("system://prompts/tool-selection-guide")
def get_tool_selection_guide() -> str:
    """
    获取工具选择指南资源
    
    Returns:
        工具选择指南文本
    """
    return TOOL_SELECTION_GUIDE


@mcp.resource("system://prompts/interaction-examples")
def get_interaction_examples() -> str:
    """
    获取交互示例资源
    
    Returns:
        交互示例文本
    """
    return INTERACTION_EXAMPLES


# ========================
# 数据库工具注册
# ========================

@mcp.tool()
def query_all_employees(limit: int = 100) -> Dict[str, Any]:
    """
    查询所有员工信息
    
    Args:
        limit: 返回结果数量限制，默认100
        
    Returns:
        员工信息列表
    """
    try:
        result = db_tools.query_all_employees(limit)
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def query_employee_by_id(employee_id: int) -> Dict[str, Any]:
    """
    根据员工ID查询员工信息
    
    Args:
        employee_id: 员工ID
        
    Returns:
        员工信息字典
    """
    try:
        result = db_tools.query_employee_by_id(employee_id)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def query_employees_by_department(department_id: int, limit: int = 100) -> Dict[str, Any]:
    """
    根据部门ID查询员工信息
    
    Args:
        department_id: 部门ID
        limit: 返回结果数量限制，默认100
        
    Returns:
        员工信息列表
    """
    try:
        result = db_tools.query_employees_by_department(department_id, limit)
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def query_employees_by_name(name: str, limit: int = 100) -> Dict[str, Any]:
    """
    根据姓名模糊查询员工信息
    
    Args:
        name: 员工姓名（支持模糊匹配）
        limit: 返回结果数量限制，默认100
        
    Returns:
        员工信息列表
    """
    try:
        result = db_tools.query_employees_by_name(name, limit)
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def query_employees_by_salary_range(
    min_salary: float, 
    max_salary: float, 
    limit: int = 100
) -> Dict[str, Any]:
    """
    根据薪资范围查询员工信息
    
    Args:
        min_salary: 最小薪资
        max_salary: 最大薪资
        limit: 返回结果数量限制，默认100
        
    Returns:
        员工信息列表
    """
    try:
        result = db_tools.query_employees_by_salary_range(min_salary, max_salary, limit)
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_department_statistics() -> Dict[str, Any]:
    """
    获取部门统计信息（员工数量、平均薪资等）
    
    Returns:
        部门统计信息列表
    """
    try:
        result = db_tools.get_department_statistics()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ========================
# 知识库工具注册
# ========================

@mcp.tool()
def search_documents(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    在知识库中搜索相关文档
    
    Args:
        query: 搜索查询
        top_k: 返回结果数量，默认5
        
    Returns:
        搜索结果列表
    """
    try:
        result = knowledge_tools.search_documents(query, top_k)
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def list_documents() -> Dict[str, Any]:
    """
    列出知识库中的所有文档
    
    Returns:
        文档列表
    """
    try:
        result = knowledge_tools.list_documents()
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_collection_info() -> Dict[str, Any]:
    """
    获取知识库集合信息
    
    Returns:
        集合信息字典
    """
    try:
        result = knowledge_tools.get_collection_info()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ========================
# 知识图谱工具注册
# ========================

@mcp.tool()
def build_knowledge_graph(content: str, filename: str) -> Dict[str, Any]:
    """
    从文档内容构建知识图谱，自动提取实体（公司、人物、产品等）和它们之间的关系
    
    Args:
        content: 文档内容
        filename: 文件名
        
    Returns:
        构建结果，包含提取的实体和关系数量
    """
    try:
        result = knowledge_graph_tools.build_graph_from_document(content, filename)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def query_entity(entity_name: str) -> Dict[str, Any]:
    """
    查询知识图谱中的实体信息及其关系
    
    使用场景：
    - 查询某个公司的详细信息和关联关系
    - 查询某个人物的职位、所属公司等
    - 查询某个产品的生产商、应用场景等
    
    Args:
        entity_name: 实体名称（如公司名、人名、产品名）
        
    Returns:
        实体信息及其所有关系
    """
    try:
        result = knowledge_graph_tools.query_entity(entity_name)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def find_entity_path(source: str, target: str) -> Dict[str, Any]:
    """
    查找两个实体之间的关系路径
    
    使用场景：
    - 查询两个公司之间的关系链
    - 查询某人和某公司之间的关系
    
    Args:
        source: 源实体名称
        target: 目标实体名称
        
    Returns:
        关系路径信息
    """
    try:
        result = knowledge_graph_tools.find_path(source, target)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def search_entities_in_graph(keyword: str = "", entity_type: str = None) -> Dict[str, Any]:
    """
    在知识图谱中搜索实体
    
    使用场景：
    - 列出所有实体：keyword="" （空字符串）
    - 搜索特定关键词：keyword="AI" 
    - 按类型过滤：entity_type="产品/服务"
    - 组合搜索：keyword="系统", entity_type="产品/服务"
    
    Args:
        keyword: 搜索关键词（默认为空，表示返回所有实体）
        entity_type: 实体类型过滤（可选），如"公司/组织"、"人物"、"产品/服务"、"技术/概念"、"地点"等
        
    Returns:
        匹配的实体列表
    """
    try:
        result = knowledge_graph_tools.search_entities(keyword, entity_type)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def list_all_entities(limit: int = 50) -> Dict[str, Any]:
    """
    列出知识图谱中的所有实体
    
    使用场景：
    - 用户问"有哪些实体"
    - 用户问"列出所有实体"
    - 用户问"查看知识图谱中的内容"
    
    Args:
        limit: 返回实体数量限制（默认50，最大100）
        
    Returns:
        实体列表，按类型分组
    """
    try:
        # 限制最大值
        limit = min(limit, 100)
        
        # 获取所有实体
        all_entities = []
        for node in list(knowledge_graph_tools.graph.nodes)[:limit]:
            node_data = knowledge_graph_tools.graph.nodes[node]
            all_entities.append({
                "name": node,
                "type": node_data.get('type', 'Unknown'),
                "description": node_data.get('description', ''),
                "source_document": node_data.get('source_document', '')
            })
        
        # 按类型分组
        entities_by_type = defaultdict(list)
        for entity in all_entities:
            entities_by_type[entity['type']].append(entity)
        
        return {
            "success": True,
            "total_count": knowledge_graph_tools.graph.number_of_nodes(),
            "returned_count": len(all_entities),
            "is_limited": knowledge_graph_tools.graph.number_of_nodes() > limit,
            "entities": all_entities,
            "entities_by_type": dict(entities_by_type)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_graph_statistics() -> Dict[str, Any]:
    """
    获取知识图谱的统计信息
    
    Returns:
        统计信息，包括实体数量、关系数量、类型分布等
    """
    try:
        result = knowledge_graph_tools.get_graph_statistics()
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def export_knowledge_graph() -> Dict[str, Any]:
    """
    导出知识图谱数据用于可视化展示
    
    Returns:
        图数据，包含nodes（节点）和edges（边）
    """
    try:
        result = knowledge_graph_tools.export_graph_data()
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def clear_knowledge_graph() -> Dict[str, Any]:
    """
    清空知识图谱（慎用！此操作会删除所有实体和关系）
    
    使用场景：
    - 需要重新构建整个知识图谱
    - 测试或重置
    
    Returns:
        清空结果
    """
    try:
        result = knowledge_graph_tools.clear_graph()
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def save_knowledge_graph() -> Dict[str, Any]:
    """
    手动保存知识图谱到磁盘（通常会自动保存）
    
    Returns:
        保存结果
    """
    try:
        success = knowledge_graph_tools.save_graph()
        return {
            "success": success,
            "message": "知识图谱已保存到磁盘" if success else "保存失败"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ========================
# 计算工具注册
# ========================

@mcp.tool()
def calculate(expression: str) -> Dict[str, Any]:
    """
    执行数学计算表达式
    
    Args:
        expression: 数学表达式字符串（如 "123 + 456"）
        
    Returns:
        计算结果字典
    """
    return calc_tools.calculate(expression)


@mcp.tool()
def statistics_analysis(numbers: list) -> Dict[str, Any]:
    """
    对数字列表进行统计分析
    
    Args:
        numbers: 数字列表
        
    Returns:
        统计分析结果字典
    """
    return calc_tools.statistics_analysis(numbers)


@mcp.tool()
def percentage_calculation(
    value: float, 
    total: float, 
    decimal_places: int = 2
) -> Dict[str, Any]:
    """
    计算百分比
    
    Args:
        value: 数值
        total: 总数
        decimal_places: 小数位数，默认2位
        
    Returns:
        百分比计算结果字典
    """
    return calc_tools.percentage_calculation(value, total, decimal_places)


# ========================
# 时间工具注册
# ========================

@mcp.tool()
def get_current_time(
    timezone: str = 'Asia/Shanghai', 
    format_str: str = None
) -> Dict[str, Any]:
    """
    获取当前时间
    
    Args:
        timezone: 时区，默认'Asia/Shanghai'
        format_str: 时间格式字符串，默认ISO格式
        
    Returns:
        当前时间信息字典
    """
    return time_tools.get_current_time(timezone, format_str)


@mcp.tool()
def date_calculation(
    base_date: str = None,
    days: int = 0,
    weeks: int = 0,
    months: int = 0,
    operation: str = "add"
) -> Dict[str, Any]:
    """
    日期计算（加减日期）
    
    Args:
        base_date: 基准日期（ISO格式或'YYYY-MM-DD'），None表示今天
        days: 天数
        weeks: 周数
        months: 月数（近似，按30天计算）
        operation: 操作类型，'add'(加) 或 'subtract'(减)
        
    Returns:
        日期计算结果字典
    """
    return time_tools.date_calculation(base_date, days, weeks, months, operation)


@mcp.tool()
def date_difference(date1: str, date2: str) -> Dict[str, Any]:
    """
    计算两个日期之间的差值
    
    Args:
        date1: 第一个日期（ISO格式或'YYYY-MM-DD'）
        date2: 第二个日期（ISO格式或'YYYY-MM-DD'）
        
    Returns:
        日期差值字典
    """
    return time_tools.date_difference(date1, date2)


@mcp.tool()
def format_timestamp(
    timestamp: float,
    format_str: str = '%Y-%m-%d %H:%M:%S',
    timezone: str = 'Asia/Shanghai'
) -> Dict[str, Any]:
    """
    将时间戳转换为格式化字符串
    
    Args:
        timestamp: Unix时间戳
        format_str: 时间格式字符串
        timezone: 时区
        
    Returns:
        格式化结果字典
    """
    return time_tools.format_timestamp(timestamp, format_str, timezone)


# ========================
# API工具注册
# ========================

@mcp.tool()
def http_request(
    url: str,
    method: str = "GET",
    headers: dict = None,
    params: dict = None,
    data: dict = None,
    json_data: dict = None
) -> Dict[str, Any]:
    """
    发送HTTP请求
    
    Args:
        url: 请求URL
        method: HTTP方法（GET, POST, PUT, DELETE等）
        headers: 请求头字典
        params: URL参数字典
        data: 表单数据字典
        json_data: JSON数据字典
        
    Returns:
        请求响应字典
    """
    return api_tools.http_request(url, method, headers, params, data, json_data)


@mcp.tool()
def get_weather(city: str = "Beijing", api_key: str = None) -> Dict[str, Any]:
    """
    查询天气信息
    
    Args:
        city: 城市名称（英文）
        api_key: OpenWeatherMap API密钥（可选）
        
    Returns:
        天气信息字典
    """
    return api_tools.get_weather(city, api_key)


@mcp.tool()
def get_ip_info(ip: str = None) -> Dict[str, Any]:
    """
    查询IP地址信息
    
    Args:
        ip: IP地址，为空则查询当前IP
        
    Returns:
        IP信息字典
    """
    return api_tools.get_ip_info(ip)


# ========================
# 服务器入口
# ========================

if __name__ == "__main__":
    logger.info(f"启动 {MCPConfig.SERVER_NAME} v{MCPConfig.SERVER_VERSION}")
    mcp.run()
