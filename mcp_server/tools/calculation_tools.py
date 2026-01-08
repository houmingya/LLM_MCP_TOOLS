"""
计算工具模块
提供数学计算和统计分析功能
"""

import logging
import math
import statistics
from typing import Union, List, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CalculationTools:
    """计算工具类"""
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """
        执行数学计算表达式
        
        Args:
            expression: 数学表达式字符串
            
        Returns:
            计算结果字典
            
        Raises:
            Exception: 计算失败时抛出异常
        """
        try:
            # 安全的数学函数白名单
            safe_dict = {
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'sum': sum,
                'pow': pow,
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'pi': math.pi,
                'e': math.e,
                'log': math.log,
                'log10': math.log10,
                'exp': math.exp,
                'ceil': math.ceil,
                'floor': math.floor,
            }
            
            # 限制表达式长度
            if len(expression) > 1000:
                raise ValueError("表达式过长，请简化后重试")
            
            # 检查危险字符
            dangerous_chars = ['__', 'import', 'exec', 'eval', 'open', 'file']
            if any(char in expression.lower() for char in dangerous_chars):
                raise ValueError("表达式包含不安全的操作")
            
            # 计算结果
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            
            logger.info(f"计算 '{expression}' = {result}")
            
            return {
                "success": True,
                "expression": expression,
                "result": result,
                "message": f"{expression} = {result}"
            }
            
        except Exception as e:
            logger.error(f"计算失败: {str(e)}")
            return {
                "success": False,
                "expression": expression,
                "error": str(e),
                "message": f"计算失败: {str(e)}"
            }
    
    def statistics_analysis(
        self, 
        numbers: List[Union[int, float]]
    ) -> Dict[str, Any]:
        """
        对数字列表进行统计分析
        
        Args:
            numbers: 数字列表
            
        Returns:
            统计分析结果字典
            
        Raises:
            Exception: 分析失败时抛出异常
        """
        try:
            if not numbers:
                raise ValueError("数字列表不能为空")
            
            if not all(isinstance(n, (int, float)) for n in numbers):
                raise ValueError("列表中包含非数字元素")
            
            result = {
                "count": len(numbers),
                "sum": sum(numbers),
                "mean": statistics.mean(numbers),
                "median": statistics.median(numbers),
                "min": min(numbers),
                "max": max(numbers),
                "range": max(numbers) - min(numbers),
            }
            
            # 只有当数据量大于1时才计算标准差和方差
            if len(numbers) > 1:
                result["stdev"] = statistics.stdev(numbers)
                result["variance"] = statistics.variance(numbers)
            else:
                result["stdev"] = 0
                result["variance"] = 0
            
            logger.info(f"对 {len(numbers)} 个数字进行统计分析")
            
            return {
                "success": True,
                "data": numbers,
                "statistics": result,
                "message": "统计分析完成"
            }
            
        except Exception as e:
            logger.error(f"统计分析失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"统计分析失败: {str(e)}"
            }
    
    def percentage_calculation(
        self,
        value: Union[int, float],
        total: Union[int, float],
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
        try:
            if total == 0:
                raise ValueError("总数不能为0")
            
            percentage = (value / total) * 100
            percentage = round(percentage, decimal_places)
            
            logger.info(f"计算百分比: {value}/{total} = {percentage}%")
            
            return {
                "success": True,
                "value": value,
                "total": total,
                "percentage": percentage,
                "message": f"{value} 占 {total} 的 {percentage}%"
            }
            
        except Exception as e:
            logger.error(f"百分比计算失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"百分比计算失败: {str(e)}"
            }


# 创建全局实例
calc_tools = CalculationTools()
