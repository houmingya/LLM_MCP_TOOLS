"""
API工具模块
提供HTTP请求、天气查询等API调用功能
"""

import logging
import requests
from typing import Dict, Any, Optional
from config.settings import ToolConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APITools:
    def get_stock_price(self, symbol: str, api_key: str = None) -> Dict[str, Any]:
        """
        查询股票当前价格（使用新浪财经公开API或可选第三方API）
        
        Args:
            symbol: 股票代码（如 'sh600519', 'sz000001'）
            api_key: 备用，部分API可能需要
        Returns:
            股票价格信息字典
        Note:
            默认使用新浪财经接口（无需API KEY），如需更高频率或更多数据可扩展
        """
        try:
            # 新浪财经接口（无需API KEY），symbol如 sh600519, sz000001
            url = f"https://hq.sinajs.cn/list={symbol}"
            headers = {"Referer": "https://finance.sina.com.cn"}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.ok and response.text:
                # 返回格式：var hq_str_sh600519="贵州茅台,1802.000,1802.000,1810.000,1820.000,1795.000,1810.000,1811.000,123456,7890,..."
                raw = response.text
                if '="' in raw:
                    parts = raw.split('="')
                    if len(parts) > 1:
                        data = parts[1].strip('";\n').split(',')
                        if len(data) >= 4:
                            name = data[0]
                            open_price = data[1]
                            prev_close = data[2]
                            price = data[3]
                            high = data[4] if len(data) > 4 else None
                            low = data[5] if len(data) > 5 else None
                            result = {
                                "success": True,
                                "symbol": symbol,
                                "name": name,
                                "price": price,
                                "open": open_price,
                                "prev_close": prev_close,
                                "high": high,
                                "low": low,
                                "message": f"{name}({symbol}) 当前价: {price} 元"
                            }
                            logger.info(result["message"])
                            return result
                return {"success": False, "symbol": symbol, "message": "未获取到股票数据"}
            else:
                return {"success": False, "symbol": symbol, "message": f"API请求失败: {response.status_code}"}
        except Exception as e:
            logger.error(f"查询股票价格失败: {str(e)}")
            return {"success": False, "symbol": symbol, "error": str(e), "message": f"查询股票价格失败: {str(e)}"}
    """API工具类"""
    
    def __init__(self):
        """初始化API工具"""
        self.timeout = ToolConfig.REQUEST_TIMEOUT
        self.user_agent = ToolConfig.USER_AGENT
        self.headers = {
            'User-Agent': self.user_agent
        }
    
    def http_request(
        self,
        url: str,
        method: str = "GET",
        headers: Dict[str, str] = None,
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        json_data: Dict[str, Any] = None
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
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        try:
            # 合并headers
            request_headers = self.headers.copy()
            if headers:
                request_headers.update(headers)
            
            # 发送请求
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=request_headers,
                params=params,
                data=data,
                json=json_data,
                timeout=self.timeout
            )
            
            # 尝试解析JSON响应
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            result = {
                "success": response.ok,
                "status_code": response.status_code,
                "url": url,
                "method": method.upper(),
                "data": response_data,
                "headers": dict(response.headers),
                "message": f"请求 {method.upper()} {url} 完成，状态码: {response.status_code}"
            }
            
            logger.info(result['message'])
            return result
            
        except Exception as e:
            logger.error(f"HTTP请求失败: {str(e)}")
            return {
                "success": False,
                "url": url,
                "method": method.upper(),
                "error": str(e),
                "message": f"请求失败: {str(e)}"
            }
    
    def get_weather(
        self,
        city: str = "Beijing",
        api_key: str = None
    ) -> Dict[str, Any]:
        """
        查询天气信息
        
        Args:
            city: 城市名称（英文）
            api_key: OpenWeatherMap API密钥（可选）
            
        Returns:
            天气信息字典
            
        Note:
            需要OpenWeatherMap API密钥才能使用此功能
            如果没有API密钥，将返回模拟数据
        """
        try:
            # 使用配置中的API密钥或传入的密钥
            key = api_key or ToolConfig.WEATHER_API_KEY
            
            if not key:
                # 返回模拟数据
                logger.warning("未配置天气API密钥，返回模拟数据")
                return {
                    "success": True,
                    "city": city,
                    "temperature": 22,
                    "description": "晴朗",
                    "humidity": 45,
                    "wind_speed": 3.5,
                    "message": f"{city} 当前天气: 晴朗, 温度 22°C (模拟数据)",
                    "note": "这是模拟数据，请配置 WEATHER_API_KEY 以获取真实天气"
                }
            
            # 调用真实的天气API
            url = ToolConfig.WEATHER_API_URL
            params = {
                'q': city,
                'appid': key,
                'units': 'metric',
                'lang': 'zh_cn'
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.ok:
                data = response.json()
                weather = data.get('weather', [{}])[0]
                main = data.get('main', {})
                wind = data.get('wind', {})
                
                result = {
                    "success": True,
                    "city": data.get('name', city),
                    "temperature": main.get('temp'),
                    "feels_like": main.get('feels_like'),
                    "description": weather.get('description'),
                    "humidity": main.get('humidity'),
                    "wind_speed": wind.get('speed'),
                    "message": f"{data.get('name', city)} 当前天气: {weather.get('description')}, 温度 {main.get('temp')}°C"
                }
                
                logger.info(result['message'])
                return result
            else:
                raise Exception(f"天气API返回错误: {response.status_code}")
                
        except Exception as e:
            logger.error(f"查询天气失败: {str(e)}")
            return {
                "success": False,
                "city": city,
                "error": str(e),
                "message": f"查询天气失败: {str(e)}"
            }
    
    def get_ip_info(self, ip: str = None) -> Dict[str, Any]:
        """
        查询IP地址信息
        
        Args:
            ip: IP地址，为空则查询当前IP
            
        Returns:
            IP信息字典
        """
        try:
            url = f"http://ip-api.com/json/{ip}" if ip else "http://ip-api.com/json/"
            
            response = requests.get(url, timeout=self.timeout)
            
            if response.ok:
                data = response.json()
                
                if data.get('status') == 'success':
                    result = {
                        "success": True,
                        "ip": data.get('query'),
                        "country": data.get('country'),
                        "city": data.get('city'),
                        "region": data.get('regionName'),
                        "isp": data.get('isp'),
                        "latitude": data.get('lat'),
                        "longitude": data.get('lon'),
                        "message": f"IP {data.get('query')}: {data.get('country')} - {data.get('city')}"
                    }
                    
                    logger.info(result['message'])
                    return result
                else:
                    raise Exception(data.get('message', '查询失败'))
            else:
                raise Exception(f"API返回错误: {response.status_code}")
                
        except Exception as e:
            logger.error(f"查询IP信息失败: {str(e)}")
            return {
                "success": False,
                "ip": ip,
                "error": str(e),
                "message": f"查询IP信息失败: {str(e)}"
            }


# 创建全局实例
api_tools = APITools()
