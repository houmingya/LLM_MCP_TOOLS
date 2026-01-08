// 知识图谱可视化脚本

let network = null;
let nodes = null;
let edges = null;
let graphData = null;

// 实体类型颜色映射
const typeColors = {
    '公司/组织': '#FF6B6B',
    '人物': '#4ECDC4',
    '产品/服务': '#45B7D1',
    '技术/概念': '#FFA07A',
    '地点': '#98D8C8',
    '时间': '#DDA15E',
    '项目/方案': '#F7DC6F',
    'Unknown': '#B8B8B8'
};

// 初始化网络图
function initNetwork() {
    // 检查 vis 是否可用
    if (typeof vis === 'undefined') {
        console.error('vis-network 库未加载');
        alert('可视化库加载失败，请刷新页面重试');
        return;
    }
    
    const container = document.getElementById('mynetwork');
    
    const data = {
        nodes: nodes,
        edges: edges
    };
    
    const options = {
        nodes: {
            shape: 'dot',
            size: 20,
            font: {
                size: 14,
                color: '#333',
                face: 'Microsoft YaHei'
            },
            borderWidth: 2,
            borderWidthSelected: 4
        },
        edges: {
            width: 2,
            color: {
                color: '#848484',
                highlight: '#667eea',
                hover: '#667eea'
            },
            arrows: {
                to: {
                    enabled: true,
                    scaleFactor: 1
                }
            },
            font: {
                size: 11,
                color: '#666',
                face: 'Microsoft YaHei',
                align: 'middle'
            },
            smooth: {
                type: 'continuous',
                roundness: 0.5
            }
        },
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -8000,
                centralGravity: 0.3,
                springLength: 150,
                springConstant: 0.04,
                damping: 0.09,
                avoidOverlap: 0.5
            },
            stabilization: {
                enabled: true,
                iterations: 100
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            navigationButtons: true,
            keyboard: true
        }
    };
    
    network = new vis.Network(container, data, options);
    
    // 节点点击事件
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            showEntityDetails(nodeId);
        }
    });
    
    // 双击事件 - 聚焦节点
    network.on('doubleClick', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            network.focus(nodeId, {
                scale: 1.5,
                animation: {
                    duration: 1000,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }
    });
}

// 加载知识图谱
async function loadGraph() {
    try {
        showLoading();
        
        const response = await fetch('/api/knowledge-graph/export');
        const result = await response.json();
        
        if (!result.success) {
            alert('加载失败: ' + (result.error || '未知错误'));
            hideLoading();
            return;
        }
        
        graphData = result;
        
        // 转换节点数据
        const nodesArray = result.nodes.map(node => ({
            id: node.id,
            label: node.label,
            title: `${node.type}\n${node.description || ''}`,
            color: typeColors[node.type] || typeColors['Unknown'],
            type: node.type,
            description: node.description,
            source_document: node.source_document
        }));
        
        // 转换边数据
        const edgesArray = result.edges.map((edge, index) => ({
            id: index,
            from: edge.source,
            to: edge.target,
            label: edge.relation,
            title: edge.description || edge.relation
        }));
        
        nodes = new vis.DataSet(nodesArray);
        edges = new vis.DataSet(edgesArray);
        
        // 更新统计信息
        updateStats(result);
        
        // 初始化或更新网络图
        if (network === null) {
            initNetwork();
        } else {
            network.setData({nodes: nodes, edges: edges});
        }
        
        hideLoading();
        
    } catch (error) {
        console.error('加载图谱失败:', error);
        alert('加载失败: ' + error.message);
        hideLoading();
    }
}

// 更新统计信息
function updateStats(data) {
    document.getElementById('nodeCount').textContent = data.nodes_count || 0;
    document.getElementById('edgeCount').textContent = data.edges_count || 0;
    
    // 统计实体类型数量
    const types = new Set(data.nodes.map(n => n.type));
    document.getElementById('typeCount').textContent = types.size;
}

// 显示实体详情
function showEntityDetails(nodeId) {
    const node = nodes.get(nodeId);
    if (!node) return;
    
    // 获取相关的边
    const connectedEdges = edges.get({
        filter: edge => edge.from === nodeId || edge.to === nodeId
    });
    
    const outgoing = connectedEdges.filter(e => e.from === nodeId);
    const incoming = connectedEdges.filter(e => e.to === nodeId);
    
    let html = `
        <div class="entity-info">
            <h4>
                <span>${node.label}</span>
                <span class="entity-type">${node.type}</span>
            </h4>
            ${node.description ? `<p style="color: #666; margin-top: 10px;">${node.description}</p>` : ''}
            ${node.source_document ? `<p style="color: #999; font-size: 0.85em; margin-top: 5px;">📄 ${node.source_document}</p>` : ''}
        </div>
    `;
    
    if (outgoing.length > 0) {
        html += '<h4 style="margin-top: 15px; color: #667eea;">📤 对外关系</h4><div class="relation-list">';
        outgoing.forEach(edge => {
            const targetNode = nodes.get(edge.to);
            html += `
                <div class="relation-item">
                    <strong>${node.label}</strong>
                    <span class="relation-arrow">→ ${edge.label} →</span>
                    <strong>${targetNode.label}</strong>
                </div>
            `;
        });
        html += '</div>';
    }
    
    if (incoming.length > 0) {
        html += '<h4 style="margin-top: 15px; color: #667eea;">📥 对内关系</h4><div class="relation-list">';
        incoming.forEach(edge => {
            const sourceNode = nodes.get(edge.from);
            html += `
                <div class="relation-item">
                    <strong>${sourceNode.label}</strong>
                    <span class="relation-arrow">→ ${edge.label} →</span>
                    <strong>${node.label}</strong>
                </div>
            `;
        });
        html += '</div>';
    }
    
    if (outgoing.length === 0 && incoming.length === 0) {
        html += '<p style="color: #999; text-align: center; margin-top: 20px;">暂无关系</p>';
    }
    
    document.getElementById('entityDetails').innerHTML = html;
}

// 搜索实体
function searchEntity(event) {
    const keyword = event.target.value.trim().toLowerCase();
    
    if (!keyword) {
        // 重置所有节点
        if (nodes) {
            nodes.forEach(node => {
                nodes.update({
                    id: node.id,
                    color: typeColors[node.type] || typeColors['Unknown']
                });
            });
        }
        return;
    }
    
    if (!nodes) return;
    
    // 高亮匹配的节点
    let foundNodes = [];
    nodes.forEach(node => {
        if (node.label.toLowerCase().includes(keyword) || 
            (node.description && node.description.toLowerCase().includes(keyword))) {
            nodes.update({
                id: node.id,
                color: '#FF0000',
                borderWidth: 4
            });
            foundNodes.push(node.id);
        } else {
            nodes.update({
                id: node.id,
                color: typeColors[node.type] || typeColors['Unknown'],
                borderWidth: 2
            });
        }
    });
    
    // 如果只有一个匹配项，聚焦到该节点
    if (foundNodes.length === 1 && network) {
        network.focus(foundNodes[0], {
            scale: 1.5,
            animation: {
                duration: 1000,
                easingFunction: 'easeInOutQuad'
            }
        });
        showEntityDetails(foundNodes[0]);
    }
}

// 适应窗口
function fitGraph() {
    if (network) {
        network.fit({
            animation: {
                duration: 1000,
                easingFunction: 'easeInOutQuad'
            }
        });
    }
}

// 导出图数据
function exportGraph() {
    if (!graphData) {
        alert('请先加载图谱');
        return;
    }
    
    const dataStr = JSON.stringify(graphData, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'knowledge_graph.json';
    link.click();
    
    URL.revokeObjectURL(url);
}

// 显示加载动画
function showLoading() {
    const container = document.getElementById('mynetwork');
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p style="color: #667eea; font-weight: 600;">正在加载知识图谱...</p>
        </div>
    `;
}

// 隐藏加载动画
function hideLoading() {
    // 加载完成后，loading会被network替换
}

// 页面加载完成后自动加载图谱
window.addEventListener('load', function() {
    loadGraph();
});
