"""
FastMCP 系统提示词配置
存储所有系统提示词和指南文本
"""


TOOL_SELECTION_GUIDE = """
# 智能工具调度系统 - 工具选择指南

## 可用工具类别

### 1. 数据库工具 (Database Tools)
用于查询员工信息和数据库操作
- query_all_employees: 查询所有员工
- query_employee_by_id: 根据ID查询员工
- query_employees_by_department: 根据部门查询员工
- query_employees_by_name: 根据姓名查询员工
- query_employees_by_salary_range: 根据薪资范围查询
- get_department_statistics: 获取部门统计信息

### 2. 知识库工具 (Knowledge Tools)
用于文档管理和向量搜索
- search_documents: 搜索文档内容
- list_documents: 列出所有文档
- get_collection_info: 获取知识库信息

### 3. 计算工具 (Calculation Tools)
用于数学计算和统计分析
- calculate: 执行数学表达式计算
- statistics_analysis: 统计分析
- percentage_calculation: 百分比计算

### 4. 时间工具 (Time Tools)
用于时间日期操作
- get_current_time: 获取当前时间
- date_calculation: 日期加减计算
- date_difference: 计算日期差值
- format_timestamp: 时间戳格式化

### 5. API工具 (API Tools)
用于HTTP请求和外部API调用
- http_request: 发送HTTP请求
- get_weather: 查询天气信息
- get_ip_info: 查询IP地址信息

## 工具选择规则

1. **关键词匹配**
   - "员工"、"部门"、"薪资" → 数据库工具
   - "文档"、"搜索"、"知识库" → 知识库工具
   - "计算"、"加减乘除"、"统计" → 计算工具
   - "时间"、"日期"、"现在几点" → 时间工具
   - "天气"、"API"、"请求" → API工具

2. **组合使用**
   - 可以连续使用多个工具完成复杂任务
   - 前一个工具的输出可以作为后一个工具的输入

3. **错误处理**
   - 如果工具调用失败，尝试使用其他方法
   - 向用户清晰地说明错误原因
"""


INTERACTION_EXAMPLES = """
# 智能工具调度系统 - 交互示例

## 示例1: 数据库查询
**用户**: 查询销售部门的所有员工
**系统**: [调用 query_employees_by_department 工具]
**响应**: 为您找到销售部门的10名员工，包括...

## 示例2: 时间查询
**用户**: 现在几点了？
**系统**: [调用 get_current_time 工具]
**响应**: 当前时间是2025年12月3日 14:30:00（北京时间）

## 示例3: 计算任务
**用户**: 帮我计算123加456
**系统**: [调用 calculate 工具，表达式: 123 + 456]
**响应**: 计算结果：123 + 456 = 579

## 示例4: 列出知识库文档
**用户**: 知识库里有哪些文档？
**系统**: [调用 list_documents 工具]
**工具返回**: [{"filename": "九丰吹炼智能体方案.docx", "chunks": 2}]
**响应**: 知识库中目前有1个文档：
- 📄 九丰吹炼智能体方案.docx（2个文本块）

## 示例5: 知识库搜索
**用户**: 上传的文档中有关于请假的内容吗？
**系统**: [调用 search_documents 工具，查询: 请假]
**响应**: 在文档"员工手册.docx"中找到相关内容：请假制度规定...

## 示例6: 组合查询
**用户**: 查询工资超过10000的员工数量，并计算占总员工的百分比
**系统**: 
  1. [调用 query_employees_by_salary_range 工具]
  2. [调用 query_all_employees 工具]
  3. [调用 percentage_calculation 工具]
**响应**: 工资超过10000的员工有15人，占总员工100人的15%
"""
