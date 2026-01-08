"""
时间工具模块
提供时间日期相关功能
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pytz

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TimeTools:
    """时间工具类"""
    
    def __init__(self):
        """初始化时间工具"""
        self.default_timezone = pytz.timezone('Asia/Shanghai')
    
    def get_current_time(
        self, 
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
            
        Raises:
            Exception: 获取时间失败时抛出异常
        """
        try:
            # 获取时区对象
            tz = pytz.timezone(timezone)
            
            # 获取当前时间
            now = datetime.now(tz)
            
            # 格式化时间
            if format_str:
                formatted_time = now.strftime(format_str)
            else:
                formatted_time = now.isoformat()
            
            result = {
                "success": True,
                "timezone": timezone,
                "timestamp": now.timestamp(),
                "iso_format": now.isoformat(),
                "formatted": formatted_time,
                "year": now.year,
                "month": now.month,
                "day": now.day,
                "hour": now.hour,
                "minute": now.minute,
                "second": now.second,
                "weekday": now.strftime("%A"),
                "message": f"当前时间: {formatted_time}"
            }
            
            logger.info(f"获取当前时间: {formatted_time}")
            return result
            
        except Exception as e:
            logger.error(f"获取当前时间失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"获取当前时间失败: {str(e)}"
            }
    
    def date_calculation(
        self,
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
            
        Raises:
            Exception: 计算失败时抛出异常
        """
        try:
            # 解析基准日期
            if base_date:
                try:
                    base_dt = datetime.fromisoformat(base_date.replace('Z', '+00:00'))
                except:
                    base_dt = datetime.strptime(base_date, '%Y-%m-%d')
            else:
                base_dt = datetime.now(self.default_timezone)
            
            # 计算时间差
            total_days = days + (weeks * 7) + (months * 30)
            
            if operation == "subtract":
                total_days = -total_days
            
            delta = timedelta(days=total_days)
            result_dt = base_dt + delta
            
            result = {
                "success": True,
                "base_date": base_dt.strftime('%Y-%m-%d'),
                "operation": operation,
                "days_changed": total_days,
                "result_date": result_dt.strftime('%Y-%m-%d'),
                "result_iso": result_dt.isoformat(),
                "weekday": result_dt.strftime("%A"),
                "message": f"从 {base_dt.strftime('%Y-%m-%d')} {operation} {total_days} 天 = {result_dt.strftime('%Y-%m-%d')}"
            }
            
            logger.info(f"日期计算: {result['message']}")
            return result
            
        except Exception as e:
            logger.error(f"日期计算失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"日期计算失败: {str(e)}"
            }
    
    def date_difference(
        self,
        date1: str,
        date2: str
    ) -> Dict[str, Any]:
        """
        计算两个日期之间的差值
        
        Args:
            date1: 第一个日期（ISO格式或'YYYY-MM-DD'）
            date2: 第二个日期（ISO格式或'YYYY-MM-DD'）
            
        Returns:
            日期差值字典
            
        Raises:
            Exception: 计算失败时抛出异常
        """
        try:
            # 解析日期
            try:
                dt1 = datetime.fromisoformat(date1.replace('Z', '+00:00'))
            except:
                dt1 = datetime.strptime(date1, '%Y-%m-%d')
            
            try:
                dt2 = datetime.fromisoformat(date2.replace('Z', '+00:00'))
            except:
                dt2 = datetime.strptime(date2, '%Y-%m-%d')
            
            # 计算差值
            diff = abs((dt2 - dt1).days)
            weeks = diff // 7
            remaining_days = diff % 7
            
            result = {
                "success": True,
                "date1": dt1.strftime('%Y-%m-%d'),
                "date2": dt2.strftime('%Y-%m-%d'),
                "total_days": diff,
                "weeks": weeks,
                "remaining_days": remaining_days,
                "message": f"{dt1.strftime('%Y-%m-%d')} 和 {dt2.strftime('%Y-%m-%d')} 相差 {diff} 天 ({weeks} 周 {remaining_days} 天)"
            }
            
            logger.info(f"日期差值计算: {result['message']}")
            return result
            
        except Exception as e:
            logger.error(f"日期差值计算失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"日期差值计算失败: {str(e)}"
            }
    
    def format_timestamp(
        self,
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
            
        Raises:
            Exception: 转换失败时抛出异常
        """
        try:
            # 获取时区对象
            tz = pytz.timezone(timezone)
            
            # 转换时间戳
            dt = datetime.fromtimestamp(timestamp, tz)
            formatted = dt.strftime(format_str)
            
            result = {
                "success": True,
                "timestamp": timestamp,
                "timezone": timezone,
                "formatted": formatted,
                "iso_format": dt.isoformat(),
                "message": f"时间戳 {timestamp} = {formatted}"
            }
            
            logger.info(f"时间戳转换: {result['message']}")
            return result
            
        except Exception as e:
            logger.error(f"时间戳转换失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"时间戳转换失败: {str(e)}"
            }


# 创建全局实例
time_tools = TimeTools()
