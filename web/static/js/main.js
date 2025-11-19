// AI Chat Guardian - 前端JavaScript

// 全局变量
let debugMode = false;

// DOM元素
const elements = {
    inputText: document.getElementById('input-text'),
    checkBtn: document.getElementById('check-btn'),
    clearBtn: document.getElementById('clear-btn'),
    demoBtn: document.getElementById('demo-btn'),
    copyBtn: document.getElementById('copy-btn'),
    progress: document.getElementById('progress'),
    resultsSection: document.getElementById('results-section'),
    safeText: document.getElementById('safe-text'),
    detectionSummary: document.getElementById('detection-summary'),
    detectionDetails: document.getElementById('detection-details'),
    debugSection: document.getElementById('debug-section'),
    llmOutput: document.getElementById('llm-output'),
    statusIndicator: document.getElementById('status-indicator'),
    llmModel: document.getElementById('llm-model')
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Chat Guardian Web 已加载');
    
    // 绑定事件
    elements.checkBtn.addEventListener('click', handleCheck);
    elements.clearBtn.addEventListener('click', handleClear);
    elements.demoBtn.addEventListener('click', handleDemo);
    elements.copyBtn.addEventListener('click', handleCopy);
    
    // 输入框快捷键
    elements.inputText.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            handleCheck();
        }
    });
    
    // 检查服务器状态
    checkServerStatus();
    
    // 每30秒检查一次状态
    setInterval(checkServerStatus, 30000);
});

// 检查服务器状态
async function checkServerStatus() {
    try {
        const response = await fetch('/api/status');
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            
            // 更新状态指示器
            elements.statusIndicator.textContent = '✓ 服务正常';
            elements.statusIndicator.classList.remove('offline');
            elements.statusIndicator.classList.add('online');
            
            // 显示LLM模型信息
            if (data.llm_enabled && data.llm_model) {
                elements.llmModel.textContent = `🤖 ${data.llm_model}`;
                elements.llmModel.style.display = 'inline-block';
            }
        }
    } catch (error) {
        console.error('状态检查失败:', error);
        elements.statusIndicator.textContent = '✗ 服务离线';
        elements.statusIndicator.classList.remove('online');
        elements.statusIndicator.classList.add('offline');
    }
}

// 处理检测按钮点击
async function handleCheck() {
    const text = elements.inputText.value.trim();
    
    if (!text) {
        showNotification('请输入要检测的文本', 'warning');
        return;
    }
    
    // 禁用按钮，显示进度
    setLoading(true);
    elements.resultsSection.style.display = 'none';
    
    try {
        const response = await fetch('/api/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result.data);
            showNotification('检测完成！', 'success');
        } else {
            showNotification(`检测失败: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('检测请求失败:', error);
        showNotification('网络错误，请检查服务器连接', 'error');
    } finally {
        setLoading(false);
    }
}

// 显示检测结果
function displayResults(data) {
    // 显示安全文本（带高亮）
    if (data.has_sensitive && data.obfuscation_details && data.obfuscation_details.length > 0) {
        // 高亮混淆的文本
        elements.safeText.innerHTML = highlightObfuscatedText(data.safe_text, data.obfuscation_details);
    } else {
        elements.safeText.textContent = data.safe_text;
    }
    
    // 显示摘要
    if (data.has_sensitive) {
        elements.detectionSummary.className = 'detection-summary';
        elements.detectionSummary.innerHTML = `
            <div class="summary-title">⚠️ 检测到 ${data.detection_count} 处敏感信息</div>
            <div>已自动混淆处理，可安全使用</div>
        `;
    } else {
        elements.detectionSummary.className = 'detection-summary safe';
        elements.detectionSummary.innerHTML = `
            <div class="summary-title">✅ 未检测到敏感信息</div>
            <div>文本可以安全使用</div>
        `;
    }
    
    // 显示详细检测结果
    if (data.has_sensitive && data.detections.length > 0) {
        displayDetectionDetails(data.detections);
    } else {
        elements.detectionDetails.innerHTML = '<p style="color: #666;">无敏感信息详情</p>';
    }
    
    // 显示LLM原始输出（调试模式）
    if (debugMode && data.llm_raw_response) {
        elements.debugSection.style.display = 'block';
        elements.llmOutput.textContent = data.llm_raw_response;
    } else {
        elements.debugSection.style.display = 'none';
    }
    
    // 显示结果区域
    elements.resultsSection.style.display = 'block';
    
    // 滚动到结果区域
    elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 高亮混淆文本
function highlightObfuscatedText(safeText, obfuscationDetails) {
    // 收集所有需要高亮的位置
    const highlights = [];
    
    for (const detail of obfuscationDetails) {
        const obfuscated = detail.obfuscated || '';
        if (!obfuscated) continue;
        
        // 在文本中查找所有出现的位置
        let pos = 0;
        while (pos < safeText.length) {
            const index = safeText.indexOf(obfuscated, pos);
            if (index === -1) break;
            
            highlights.push({
                start: index,
                end: index + obfuscated.length,
                text: obfuscated
            });
            
            pos = index + obfuscated.length;
        }
    }
    
    // 按位置排序并去重
    highlights.sort((a, b) => a.start - b.start);
    
    // 合并重叠的高亮区域
    const merged = [];
    for (const h of highlights) {
        if (merged.length === 0 || merged[merged.length - 1].end < h.start) {
            merged.push(h);
        } else {
            // 合并重叠区域
            merged[merged.length - 1].end = Math.max(merged[merged.length - 1].end, h.end);
        }
    }
    
    // 构建HTML
    let result = '';
    let lastPos = 0;
    
    for (const h of merged) {
        // 添加未高亮的部分
        if (h.start > lastPos) {
            result += escapeHtml(safeText.substring(lastPos, h.start));
        }
        
        // 添加高亮的部分
        const highlightedText = escapeHtml(safeText.substring(h.start, h.end));
        result += `<span class="obfuscated-text">${highlightedText}</span>`;
        
        lastPos = h.end;
    }
    
    // 添加剩余文本
    if (lastPos < safeText.length) {
        result += escapeHtml(safeText.substring(lastPos));
    }
    
    return result;
}

// 显示检测详情
function displayDetectionDetails(detections) {
    // 按类型分组
    const groups = {};
    detections.forEach(det => {
        const type = det.type || '未知';
        if (!groups[type]) {
            groups[type] = [];
        }
        groups[type].push(det);
    });
    
    // 生成HTML
    let html = '<div class="detection-groups">';
    
    for (const [type, items] of Object.entries(groups)) {
        html += `
            <div class="detection-group">
                <div class="detection-group-title">[${type}] 共 ${items.length} 处:</div>
        `;
        
        items.forEach((item, index) => {
            const content = item.content.length > 50 
                ? item.content.substring(0, 50) + '...' 
                : item.content;
            const confidence = (item.confidence * 100).toFixed(1);
            const start = item.start !== undefined ? item.start : 'N/A';
            const end = item.end !== undefined ? item.end : 'N/A';
            
            html += `
                <div class="detection-item">
                    <div class="detection-content">${index + 1}. ${escapeHtml(content)}</div>
                    <div class="detection-meta">
                        置信度: ${confidence}% | 位置: ${start}-${end}
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
    }
    
    html += '</div>';
    elements.detectionDetails.innerHTML = html;
}

// 处理清空按钮
function handleClear() {
    elements.inputText.value = '';
    elements.resultsSection.style.display = 'none';
    elements.inputText.focus();
    showNotification('已清空', 'info');
}

// 处理示例按钮 - 随机加载不同类型的示例
function handleDemo() {
    // 定义多种专注不同检测场景的示例文本
    const demoExamples = [
        {
            name: '代码泄密场景',
            text: `我在开发一个Python项目，遇到了数据库连接问题，代码如下：

import mysql.connector

# 连接数据库
conn = mysql.connector.connect(
    host="db.company.com",
    user="admin",
    password="CompanyDB@2024!Secret",
    database="production"
)

# API配置
API_KEY = "sk-proj-abc123def456ghi789"
SECRET_TOKEN = "ghp_1234567890abcdefghijklmnopqr"

这段代码为什么连接不上？帮我看看问题在哪里。`
        },
        {
            name: '财务分析场景',
            text: `帮我分析一下这份财务数据，看看有什么问题：

我们公司Q4的业绩出来了：
- 总营收8500万，比去年同期增长42%
- 净利润1200万
- 最大的两个客户是阿里巴巴350万和腾讯280万的合同
- 研发人员工资是大头，一年2800万
- 明年Q1我们定的目标是2500万营收

财务王芳说这个增长速度可以，但我觉得利润率有点低。你觉得呢？应该怎么优化成本？`
        },
        {
            name: '客户跟进场景',
            text: `我在整理客户跟进情况，帮我写个客户拜访总结：

这周见了两个重点客户：

第一个是北京创新科技的张总，他手机是13800138000，邮箱zhang.ceo@bjcxtech.com，身份证110105198506123456。他们有一笔500万订单的意向，说这个月底给决策。

第二个是上海智能制造的李经理，公司电话021-65432109，微信是li_manager_sh，打款账号是6222 0012 3456 7890。他们已经签了意向书了。

你帮我总结一下，怎么写这个跟进报告比较专业？`
        },
        {
            name: '服务器部署场景',
            text: `我要部署一个新服务，把生产环境配置给你看看，你帮我检查下有没有安全问题：

数据库服务器：
- IP: 172.16.88.100
- 用户: root
- 密码: Prod_MySQL#2024
- 端口: 3306

Redis配置：
redis://172.16.88.101:6379
密码是Redis@Prod!2024

还有API网关 https://api.company.com
Token: sk-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
AWS的Key是AKIAIOSFODNN7EXAMPLE
Secret: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

这样配置有问题吗？需要注意什么？`
        },
        {
            name: '无敏感场景',
            text: `我在使用 Freeimage API，这个API可以帮我处理图片，比如调整大小、裁剪、添加水印等功能。它支持多种图片格式，包括JPEG、PNG、BMP等。

我想用它来做一个简单的图片处理工具，用户可以上传图片，然后选择需要的操作，比如调整大小或者添加水印，最后下载处理后的图片。

请帮我写一段代码示例，展示如何使用 Freeimage API 来实现这个功能。`
        }
    ];
    
    // 随机选择一个示例
    const randomIndex = Math.floor(Math.random() * demoExamples.length);
    const selectedDemo = demoExamples[randomIndex];
    
    elements.inputText.value = selectedDemo.text;
    elements.inputText.focus();
    showNotification(`已加载随机示例：${selectedDemo.name}`, 'info');
}

// 处理复制按钮
function handleCopy() {
    const text = elements.safeText.textContent;
    
    if (!text) {
        showNotification('没有可复制的内容', 'warning');
        return;
    }
    
    navigator.clipboard.writeText(text).then(() => {
        showNotification('已复制到剪贴板', 'success');
    }).catch(err => {
        console.error('复制失败:', err);
        showNotification('复制失败，请手动复制', 'error');
    });
}

// 设置加载状态
function setLoading(loading) {
    elements.checkBtn.disabled = loading;
    elements.progress.style.display = loading ? 'block' : 'none';
    
    if (loading) {
        elements.checkBtn.innerHTML = '<span class="btn-icon">⏳</span><span class="btn-text">检测中...</span>';
    } else {
        elements.checkBtn.innerHTML = '<span class="btn-icon">🔍</span><span class="btn-text">检测并混淆</span>';
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    // 简单的通知实现
    const colors = {
        success: '#4CAF50',
        error: '#f44336',
        warning: '#FF9800',
        info: '#2196F3'
    };
    
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 切换调试模式
function toggleDebug() {
    debugMode = !debugMode;
    showNotification(debugMode ? '调试模式已开启' : '调试模式已关闭', 'info');
    
    // 如果有结果，重新显示以更新调试信息
    if (elements.resultsSection.style.display !== 'none') {
        elements.debugSection.style.display = debugMode ? 'block' : 'none';
    }
}

// 显示帮助
function showHelp() {
    const helpText = `
【使用帮助】

1. 输入文本：在文本框中输入需要检测的内容
2. 点击"检测并混淆"：系统会自动检测敏感信息并进行混淆
3. 查看结果：在"安全文本"区域查看混淆后的文本
4. 复制使用：点击"复制"按钮将安全文本复制到剪贴板

【快捷键】
- Ctrl+Enter: 执行检测
- Ctrl+C: 复制结果

【支持的敏感信息类型】
- 财务信息：金额、营收、利润等
- 人员信息：姓名、工号、联系方式等
- 技术信息：密钥、密码、IP地址等
- 客户信息：客户数据、合同信息等
- 战略信息：商业计划、机密项目等
    `.trim();
    
    alert(helpText);
}

// 显示关于
function showAbout() {
    const aboutText = `
【AI Chat Guardian】
版本：Web 1.0
类型：内网测试版

这是一个企业级敏感信息检测与保护系统，
帮助您在分享文本前自动识别并混淆敏感信息。
    `.trim();
    
    alert(aboutText);
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ========== 配置管理功能 ==========

// 打开配置面板
function openConfigModal() {
    const modal = document.getElementById('config-modal');
    modal.style.display = 'flex';
    loadConfig(); // 加载当前配置
}

// 关闭配置面板
function closeConfigModal() {
    const modal = document.getElementById('config-modal');
    modal.style.display = 'none';
}

// 加载配置
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const result = await response.json();
        
        if (result.success) {
            const config = result.data;
            
            // 设置基础检测器开关
            document.getElementById('enable-regex').checked = config.detection.enable_regex;
            document.getElementById('enable-keyword').checked = config.detection.enable_keyword;
            document.getElementById('enable-ai').checked = config.detection.enable_ai;
            
            // 设置LLM检测器开关
            const llmEnabled = config.llm_detector.enable;
            document.getElementById('enable-llm').checked = llmEnabled;
            
            // 设置LLM类型
            const llmType = config.llm_detector.type || 'api';
            document.querySelector(`input[name="llm-type"][value="${llmType}"]`).checked = true;
            
            // 设置API提供商
            if (config.llm_detector.api && config.llm_detector.api.provider) {
                document.getElementById('api-provider').value = config.llm_detector.api.provider;
            }
            
            // 设置本地模型
            if (config.llm_detector.local && config.llm_detector.local.model) {
                document.getElementById('local-model').value = config.llm_detector.local.model;
            }
            
            // 更新显示
            toggleLLMConfig();
            updateLLMTypeDisplay();
            
            // 更新当前状态
            updateDetectorStatus(config.current_status);
        } else {
            showNotification('加载配置失败: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('加载配置失败:', error);
        showNotification('加载配置失败: ' + error.message, 'error');
    }
}

// 保存配置
async function saveConfig() {
    try {
        // 收集配置数据
        const config = {
            detection: {
                enable_regex: document.getElementById('enable-regex').checked,
                enable_keyword: document.getElementById('enable-keyword').checked,
                enable_ai: document.getElementById('enable-ai').checked
            },
            llm_detector: {
                enable: document.getElementById('enable-llm').checked,
                type: document.querySelector('input[name="llm-type"]:checked').value
            }
        };
        
        // 根据LLM类型添加相应配置
        if (config.llm_detector.type === 'api') {
            config.llm_detector.api = {
                provider: document.getElementById('api-provider').value
            };
        } else if (config.llm_detector.type === 'local') {
            config.llm_detector.local = {
                model: document.getElementById('local-model').value
            };
        }
        
        // 显示保存中提示
        showNotification('正在保存配置并重新加载检测器...', 'info');
        
        // 发送保存请求
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('配置已保存并应用成功！', 'success');
            closeConfigModal();
            
            // 刷新服务器状态
            setTimeout(checkServerStatus, 1000);
        } else {
            showNotification('保存配置失败: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('保存配置失败:', error);
        showNotification('保存配置失败: ' + error.message, 'error');
    }
}

// 切换LLM配置面板显示
function toggleLLMConfig() {
    const llmEnabled = document.getElementById('enable-llm').checked;
    const llmPanel = document.getElementById('llm-config-panel');
    llmPanel.style.display = llmEnabled ? 'block' : 'none';
}

// 更新LLM类型显示
function updateLLMTypeDisplay() {
    const llmType = document.querySelector('input[name="llm-type"]:checked').value;
    const apiConfig = document.getElementById('api-config');
    const localConfig = document.getElementById('local-config');
    
    if (llmType === 'api') {
        apiConfig.style.display = 'block';
        localConfig.style.display = 'none';
    } else {
        apiConfig.style.display = 'none';
        localConfig.style.display = 'block';
    }
}

// 更新检测器状态显示
function updateDetectorStatus(status) {
    const statusMap = {
        'status-regex': status.regex_active,
        'status-keyword': status.keyword_active,
        'status-ai': status.ai_active,
        'status-llm': status.llm_active
    };
    
    for (const [id, active] of Object.entries(statusMap)) {
        const element = document.getElementById(id);
        if (active) {
            element.textContent = '✅ 已启用';
            element.className = 'status-value status-active';
        } else {
            element.textContent = '❌ 已禁用';
            element.className = 'status-value status-inactive';
        }
    }
    
    // 显示LLM模型信息
    const llmStatus = document.getElementById('status-llm');
    if (status.llm_active && status.llm_model) {
        llmStatus.textContent = `✅ 已启用 (${status.llm_type === 'api' ? 'API' : status.llm_model})`;
    }
}

// 绑定配置按钮事件
document.addEventListener('DOMContentLoaded', function() {
    const configBtn = document.getElementById('config-btn');
    if (configBtn) {
        configBtn.addEventListener('click', openConfigModal);
    }
    
    // 点击模态框外部关闭
    const modal = document.getElementById('config-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeConfigModal();
            }
        });
    }
});
