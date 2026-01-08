// 工具函数模块

/**
 * 显示状态提示
 * @param {string} message - 提示消息
 * @param {string} type - 提示类型 ('connected', 'disconnected', 'error')
 * @param {number} duration - 显示时长（毫秒），默认3000ms
 */
function showStatus(message, type, duration = 3000) {
    // 移除旧的状态提示
    const oldStatus = document.querySelector('.status');
    if (oldStatus) oldStatus.remove();

    // 创建新的状态提示
    const status = document.createElement('div');
    status.className = `status ${type}`;
    
    // 支持多行消息
    if (message.includes('\n')) {
        message.split('\n').forEach((line, index) => {
            if (index > 0) status.appendChild(document.createElement('br'));
            status.appendChild(document.createTextNode(line));
        });
    } else {
        status.textContent = message;
    }
    
    document.body.appendChild(status);

    // 自动移除（如果duration为0则不自动移除）
    if (duration > 0) {
        setTimeout(() => {
            status.remove();
        }, duration);
    }
}

/**
 * HTML转义
 * @param {string} text - 要转义的文本
 * @returns {string} 转义后的HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

/**
 * Markdown 渲染函数
 * @param {string} text - Markdown 文本
 * @returns {string} 渲染后的HTML
 */
function renderMarkdown(text) {
    if (!text) return '';
    
    // 配置 marked.js
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true,        // 支持换行
            gfm: true,          // 支持 GitHub Flavored Markdown
            headerIds: false,   // 不生成 header id
            mangle: false       // 不混淆邮箱地址
        });
        
        try {
            return marked.parse(text);
        } catch (e) {
            console.error('Markdown 渲染失败:', e);
            return escapeHtml(text);
        }
    } else {
        // 如果 marked.js 未加载，使用简单的格式化
        return escapeHtml(text);
    }
}

/**
 * 更新进度条
 * @param {number} progress - 进度百分比 (0-100)
 */
function updateProgressBar(progress) {
    // 这是一个占位函数，用于状态显示中的进度
    // 实际上我们通过showStatus来显示进度信息
    console.log(`进度: ${progress}%`);
}

