// WebSocket 连接管理模块

let ws = null;
let isConnected = false;

/**
 * 初始化WebSocket连接
 */
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        isConnected = true;
        showStatus('已连接', 'connected');
        console.log('WebSocket连接成功');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };

    ws.onclose = () => {
        isConnected = false;
        showStatus('连接断开', 'disconnected');
        console.log('WebSocket连接断开');
        // 3秒后重连
        setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
        showStatus('连接错误', 'error');
        console.error('WebSocket错误:', error);
    };
}

/**
 * 发送WebSocket消息
 * @param {Object} data - 要发送的数据
 */
function sendWebSocketMessage(data) {
    if (ws && isConnected) {
        ws.send(JSON.stringify(data));
        return true;
    }
    return false;
}

/**
 * 获取连接状态
 * @returns {boolean} 是否已连接
 */
function getConnectionStatus() {
    return isConnected;
}
