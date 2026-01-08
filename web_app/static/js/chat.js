// 聊天界面交互模块

/**
 * 发送消息
 */
function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message) return;
    if (!getConnectionStatus()) {
        showStatus('未连接到服务器', 'error');
        return;
    }

    // 显示用户消息
    addUserMessage(message);

    // 发送到服务器
    sendWebSocketMessage({
        type: 'user_message',
        content: message
    });

    // 清空输入框并禁用发送按钮
    input.value = '';
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<div class="loading"></div>';
}

/**
 * 添加用户消息到聊天容器
 * @param {string} message - 用户消息内容
 */
function addUserMessage(message) {
    const chatContainer = document.getElementById('chatContainer');
    const userMsg = document.createElement('div');
    userMsg.className = 'message user';
    userMsg.innerHTML = `
        <div class="avatar">👤</div>
        <div class="message-content">${escapeHtml(message)}</div>
    `;
    chatContainer.appendChild(userMsg);
    scrollToBottom();
}

/**
 * 添加助手消息到聊天容器
 * @param {string} content - 助手消息内容
 */
function addAssistantMessage(content) {
    const chatContainer = document.getElementById('chatContainer');
    const assistantMsg = document.createElement('div');
    assistantMsg.className = 'message assistant';
    assistantMsg.innerHTML = `
        <div class="avatar">🤖</div>
        <div class="message-content markdown-content">${renderMarkdown(content)}</div>
    `;
    chatContainer.appendChild(assistantMsg);
    scrollToBottom();
}

/**
 * 添加系统消息到聊天容器
 * @param {string} content - 系统消息内容
 * @param {string} avatar - 头像图标
 */
function addSystemMessage(content, avatar = '💡') {
    const chatContainer = document.getElementById('chatContainer');
    const systemMsg = document.createElement('div');
    systemMsg.className = 'message system';
    systemMsg.innerHTML = `
        <div class="avatar">${avatar}</div>
        <div class="message-content">${content}</div>
    `;
    chatContainer.appendChild(systemMsg);
    scrollToBottom();
}

/**
 * 添加工具调用消息
 * @param {string} toolName - 工具名称
 * @param {Object} toolArgs - 工具参数
 */
function addToolCallMessage(toolName, toolArgs) {
    const chatContainer = document.getElementById('chatContainer');
    const toolMsg = document.createElement('div');
    toolMsg.className = 'message system';
    toolMsg.innerHTML = `
        <div class="avatar">🔧</div>
        <div class="message-content">
            <div class="tool-call">
                <strong>调用工具:</strong> ${toolName}<br>
                <strong>参数:</strong> ${JSON.stringify(toolArgs, null, 2)}
            </div>
        </div>
    `;
    chatContainer.appendChild(toolMsg);
    scrollToBottom();
}

/**
 * 添加工具结果消息
 * @param {string} toolName - 工具名称
 * @param {Object} result - 工具结果
 */
function addToolResultMessage(toolName, result) {
    const chatContainer = document.getElementById('chatContainer');
    const resultMsg = document.createElement('div');
    resultMsg.className = 'message system';
    resultMsg.innerHTML = `
        <div class="avatar">✅</div>
        <div class="message-content">
            <div class="tool-result">
                <strong>工具结果:</strong> ${toolName}<br>
                <pre>${JSON.stringify(result, null, 2)}</pre>
            </div>
        </div>
    `;
    chatContainer.appendChild(resultMsg);
    scrollToBottom();
}

/**
 * 恢复发送按钮状态
 */
function enableSendButton() {
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = false;
    sendBtn.textContent = '发送';
}

/**
 * 处理回车键
 * @param {KeyboardEvent} event - 键盘事件
 */
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

/**
 * 清除对话历史
 */
function clearHistory() {
    if (!getConnectionStatus()) {
        showStatus('未连接到服务器', 'error');
        return;
    }

    // 确认对话框
    if (confirm('确定要清除所有对话历史吗？')) {
        // 发送清除历史消息
        sendWebSocketMessage({
            type: 'clear_history'
        });

        // 清空聊天容器（保留欢迎消息）
        const chatContainer = document.getElementById('chatContainer');
        chatContainer.innerHTML = `
            <div class="message system">
                <div class="avatar">💡</div>
                <div class="message-content">
                    <strong>欢迎使用智能工具调度系统！</strong><br><br>
                    我可以帮你：<br>
                    • 查询员工信息和数据库数据<br>
                    • 搜索上传的文档内容<br>
                    • 进行数学计算和统计分析<br>
                    • 获取时间日期信息<br>
                    • 查询天气等外部API<br><br>
                    请随意提问，我会自动选择合适的工具来帮助你！
                </div>
            </div>
        `;

        showStatus('对话历史已清除', 'connected');
    }
}

/**
 * 滚动到底部
 */
function scrollToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
