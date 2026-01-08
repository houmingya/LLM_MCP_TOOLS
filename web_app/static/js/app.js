// 主应用入口文件

/**
 * 初始化应用
 */
function initApp() {
    // 初始化WebSocket连接
    connectWebSocket();
    
    // 初始化文件上传
    initFileUpload();
    
    // 加载文档列表
    loadDocuments();
    
    console.log('应用初始化完成');
}

// 页面加载完成后初始化应用
window.addEventListener('load', initApp);
