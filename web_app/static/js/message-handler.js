// 消息处理模块

/**
 * 处理接收到的WebSocket消息
 * @param {Object} data - 接收到的消息数据
 */
function handleMessage(data) {
    switch (data.type) {
        case 'tool_call':
            handleToolCall(data);
            break;
        
        case 'tool_result':
            handleToolResult(data);
            break;
        
        case 'assistant_message':
            handleAssistantMessage(data);
            break;
        
        case 'error':
            handleError(data);
            break;
        
        case 'system_message':
            handleSystemMessage(data);
            break;
        
        case 'upload_progress':
            handleUploadProgress(data);
            break;
        
        default:
            console.warn('未知的消息类型:', data.type);
    }
}

/**
 * 处理工具调用消息
 * @param {Object} data - 工具调用数据
 */
function handleToolCall(data) {
    addToolCallMessage(data.tool_name, data.tool_args);
}

/**
 * 处理工具结果消息
 * @param {Object} data - 工具结果数据
 */
function handleToolResult(data) {
    addToolResultMessage(data.tool_name, data.result);
}

/**
 * 处理助手回复消息
 * @param {Object} data - 助手消息数据
 */
function handleAssistantMessage(data) {
    addAssistantMessage(data.content);
    enableSendButton();
}

/**
 * 处理错误消息
 * @param {Object} data - 错误数据
 */
function handleError(data) {
    showStatus('错误: ' + data.content, 'error');
    enableSendButton();
}

/**
 * 处理系统消息
 * @param {Object} data - 系统消息数据
 */
function handleSystemMessage(data) {
    showStatus(data.content, 'connected', 3000);
}

/**
 * 处理上传进度消息
 * @param {Object} data - 进度数据
 */
function handleUploadProgress(data) {
    const { stage, message, progress, current, total } = data;
    
    // 构建详细的进度消息
    let displayMessage = message;
    if (current && total) {
        displayMessage += ` (${current}/${total})`;
    }
    
    // 根据阶段显示不同的状态
    let statusType = 'connected';
    if (stage === 'error') {
        statusType = 'error';
    } else if (stage === 'completed') {
        statusType = 'connected';
    }
    
    // 显示进度
    showStatus(displayMessage, statusType, 0);
    
    // 如果有进度百分比，更新进度条（如果存在）
    if (progress !== undefined) {
        updateProgressBar(progress);
    }
}
