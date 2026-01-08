// 文件上传管理模块

/**
 * 初始化文件上传功能
 */
function initFileUpload() {
    document.getElementById('fileInput').addEventListener('change', handleFileSelect);
}

/**
 * 处理文件选择事件
 * @param {Event} event - 文件选择事件
 */
async function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    
    // 获取知识图谱开关状态
    const buildGraph = document.getElementById('buildGraphCheck').checked;
    formData.append('build_graph', buildGraph);

    try {
        // 显示上传进度
        showStatus('📤 正在上传文档...', 'connected', 0);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        
        if (result.success) {
            let message = `✅ 文档上传成功！\n📝 已分割为 ${result.chunks} 个文本块`;
            let duration = 5000;
            
            // 显示知识图谱构建结果
            if (buildGraph) {
                if (result.knowledge_graph) {
                    const kg = result.knowledge_graph;
                    if (kg.success) {
                        // 显示详细的增量更新信息
                        const newEntities = kg.new_entities || 0;
                        const updatedEntities = kg.updated_entities || 0;
                        const newRelations = kg.new_relations || 0;
                        const updatedRelations = kg.updated_relations || 0;
                        
                        message += `\n🧠 知识图谱${newEntities > 0 || newRelations > 0 ? '增量更新' : '更新'}成功`;
                        
                        if (newEntities > 0 || updatedEntities > 0) {
                            message += `\n   实体: `;
                            if (newEntities > 0) message += `➕${newEntities}新增 `;
                            if (updatedEntities > 0) message += `🔄${updatedEntities}更新 `;
                            message += `(共${kg.total_nodes}个)`;
                        }
                        
                        if (newRelations > 0 || updatedRelations > 0) {
                            message += `\n   关系: `;
                            if (newRelations > 0) message += `➕${newRelations}新增 `;
                            if (updatedRelations > 0) message += `🔄${updatedRelations}更新 `;
                            message += `(共${kg.total_edges}条)`;
                        }
                        
                        // 持久化状态
                        if (kg.persisted) {
                            message += `\n   💾 已保存到磁盘`;
                        }
                        
                        // 如果有跳过的关系，显示警告
                        if (kg.skipped_relations_count && kg.skipped_relations_count > 0) {
                            message += `\n⚠️ 跳过 ${kg.skipped_relations_count} 条关系（实体不存在）`;
                            duration = 8000;  // 延长显示时间以便用户看到警告
                        } else {
                            duration = 7000;
                        }
                    } else {
                        message += `\n⚠️ 知识图谱构建失败: ${kg.error || '未知错误'}`;
                        duration = 8000;
                    }
                } else if (result.knowledge_graph_error) {
                    message += `\n⚠️ 知识图谱构建失败: ${result.knowledge_graph_error}`;
                    duration = 8000;
                }
            } else {
                message += '\n💡 未构建知识图谱（已禁用）';
            }
            
            showStatus(message, 'connected', duration);
            loadDocuments();
        } else {
            showStatus('❌ 上传失败: ' + result.message, 'error', 5000);
        }
    } catch (error) {
        showStatus('❌ 上传错误: ' + error.message, 'error', 5000);
    }

    // 清空文件选择
    event.target.value = '';
}

/**
 * 加载文档列表
 */
async function loadDocuments() {
    try {
        const response = await fetch('/documents');
        const result = await response.json();
        
        if (result.success) {
            const count = result.documents.length;
            document.getElementById('docCount').textContent = `文档: ${count}`;
        }
    } catch (error) {
        console.error('加载文档列表失败:', error);
    }
}

/**
 * 触发文件选择对话框
 */
function triggerFileUpload() {
    document.getElementById('fileInput').click();
}
