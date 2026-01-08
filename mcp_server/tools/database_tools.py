"""
数据库工具模块
提供员工信息查询等数据库操作功能
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import pymysql
from pymysql.cursors import DictCursor
from config.settings import DatabaseConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseTools:
    """数据库工具类"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.config = DatabaseConfig.to_dict()
    
    def _convert_dates(self, data: Any) -> Any:
        """
        递归转换数据中的日期/时间对象为字符串
        
        Args:
            data: 要转换的数据（字典、列表或其他类型）
            
        Returns:
            转换后的数据
        """
        if isinstance(data, dict):
            return {key: self._convert_dates(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._convert_dates(item) for item in data]
        elif isinstance(data, (date, datetime)):
            return data.isoformat()
        else:
            return data
    
    def _get_connection(self) -> pymysql.Connection:
        """
        获取数据库连接
        
        Returns:
            数据库连接对象
        """
        try:
            connection = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                charset=self.config['charset'],
                cursorclass=DictCursor
            )
            return connection
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise
    
    def query_all_employees(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        查询所有员工信息
        
        Args:
            limit: 返回结果数量限制，默认100
            
        Returns:
            员工信息列表
            
        Raises:
            Exception: 查询失败时抛出异常
        """
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                sql = """
                    SELECT 
                        employee_id,
                        first_name,
                        last_name,
                        email,
                        phone_number,
                        hire_date,
                        job_id,
                        salary,
                        department_id
                    FROM employees
                    LIMIT %s
                """
                cursor.execute(sql, (limit,))
                results = cursor.fetchall()
                logger.info(f"查询到 {len(results)} 条员工记录")
                return self._convert_dates(results)
        except Exception as e:
            logger.error(f"查询所有员工失败: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    def query_employee_by_id(self, employee_id: int) -> Optional[Dict[str, Any]]:
        """
        根据员工ID查询员工信息
        
        Args:
            employee_id: 员工ID
            
        Returns:
            员工信息字典，如果不存在返回None
            
        Raises:
            Exception: 查询失败时抛出异常
        """
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                sql = """
                    SELECT 
                        employee_id,
                        first_name,
                        last_name,
                        email,
                        phone_number,
                        hire_date,
                        job_id,
                        salary,
                        department_id
                    FROM employees
                    WHERE employee_id = %s
                """
                cursor.execute(sql, (employee_id,))
                result = cursor.fetchone()
                if result:
                    logger.info(f"查询到员工 {employee_id} 的信息")
                else:
                    logger.info(f"未找到员工 {employee_id}")
                return self._convert_dates(result)
        except Exception as e:
            logger.error(f"根据ID查询员工失败: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    def query_employees_by_department(
        self, 
        department_id: int, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        根据部门ID查询员工信息
        
        Args:
            department_id: 部门ID
            limit: 返回结果数量限制，默认100
            
        Returns:
            员工信息列表
            
        Raises:
            Exception: 查询失败时抛出异常
        """
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                sql = """
                    SELECT 
                        employee_id,
                        first_name,
                        last_name,
                        email,
                        phone_number,
                        hire_date,
                        job_id,
                        salary,
                        department_id
                    FROM employees
                    WHERE department_id = %s
                    LIMIT %s
                """
                cursor.execute(sql, (department_id, limit))
                results = cursor.fetchall()
                logger.info(f"部门 {department_id} 查询到 {len(results)} 条员工记录")
                return self._convert_dates(results)
        except Exception as e:
            logger.error(f"根据部门查询员工失败: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    def query_employees_by_name(
        self, 
        name: str, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        根据姓名模糊查询员工信息
        
        Args:
            name: 员工姓名（支持模糊匹配）
            limit: 返回结果数量限制，默认100
            
        Returns:
            员工信息列表
            
        Raises:
            Exception: 查询失败时抛出异常
        """
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                sql = """
                    SELECT 
                        employee_id,
                        first_name,
                        last_name,
                        email,
                        phone_number,
                        hire_date,
                        job_id,
                        salary,
                        department_id
                    FROM employees
                    WHERE first_name LIKE %s OR last_name LIKE %s
                    LIMIT %s
                """
                search_pattern = f"%{name}%"
                cursor.execute(sql, (search_pattern, search_pattern, limit))
                results = cursor.fetchall()
                logger.info(f"姓名包含 '{name}' 的员工有 {len(results)} 条记录")
                return self._convert_dates(results)
        except Exception as e:
            logger.error(f"根据姓名查询员工失败: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    def query_employees_by_salary_range(
        self,
        min_salary: float,
        max_salary: float,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        根据薪资范围查询员工信息
        
        Args:
            min_salary: 最小薪资
            max_salary: 最大薪资
            limit: 返回结果数量限制，默认100
            
        Returns:
            员工信息列表
            
        Raises:
            Exception: 查询失败时抛出异常
        """
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                sql = """
                    SELECT 
                        employee_id,
                        first_name,
                        last_name,
                        email,
                        phone_number,
                        hire_date,
                        job_id,
                        salary,
                        department_id
                    FROM employees
                    WHERE salary BETWEEN %s AND %s
                    ORDER BY salary DESC
                    LIMIT %s
                """
                cursor.execute(sql, (min_salary, max_salary, limit))
                results = cursor.fetchall()
                logger.info(f"薪资范围 {min_salary}-{max_salary} 的员工有 {len(results)} 条记录")
                return self._convert_dates(results)
        except Exception as e:
            logger.error(f"根据薪资范围查询员工失败: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    def get_department_statistics(self) -> List[Dict[str, Any]]:
        """
        获取部门统计信息（员工数量、平均薪资等）
        
        Returns:
            部门统计信息列表
            
        Raises:
            Exception: 查询失败时抛出异常
        """
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                sql = """
                    SELECT 
                        department_id,
                        COUNT(*) as employee_count,
                        AVG(salary) as avg_salary,
                        MIN(salary) as min_salary,
                        MAX(salary) as max_salary
                    FROM employees
                    WHERE department_id IS NOT NULL
                    GROUP BY department_id
                    ORDER BY employee_count DESC
                """
                cursor.execute(sql)
                results = cursor.fetchall()
                logger.info(f"获取到 {len(results)} 个部门的统计信息")
                return self._convert_dates(results)
        except Exception as e:
            logger.error(f"获取部门统计信息失败: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()


# 创建全局实例
db_tools = DatabaseTools()
