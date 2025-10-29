// 通用工具函数
class TestPlatformUtils {
    // 验证JSON格式
    static isValidJSON(str) {
        try {
            JSON.parse(str);
            return true;
        } catch (e) {
            return false;
        }
    }

    // 格式化JSON字符串
    static formatJSON(str) {
        try {
            const obj = JSON.parse(str);
            return JSON.stringify(obj, null, 4);
        } catch (e) {
            return str;
        }
    }

    // 显示消息
    static showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        messageDiv.textContent = message;

        // 添加样式
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 4px;
            color: white;
            z-index: 1000;
            max-width: 400px;
            animation: slideIn 0.3s ease-out;
        `;

        // 设置颜色
        const colors = {
            info: '#3498db',
            success: '#27ae60',
            warning: '#f39c12',
            error: '#e74c3c'
        };
        messageDiv.style.backgroundColor = colors[type] || colors.info;

        document.body.appendChild(messageDiv);

        // 3秒后自动消失
        setTimeout(() => {
            messageDiv.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 300);
        }, 3000);
    }

    // 加载测试用例数据
    static async loadTestCase(caseName) {
        try {
            const response = await fetch(`/api/test-cases/${caseName}`);
            if (response.ok) {
                const data = await response.json();
                return data;
            }
            return null;
        } catch (error) {
            console.error('加载测试用例失败:', error);
            return null;
        }
    }

    // 下载测试报告
    static downloadReport(filename) {
        const link = document.createElement('a');
        link.href = `/api/reports/${filename}`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// 测试用例管理相关功能
class TestCaseManager {
    constructor() {
        this.initEventListeners();
    }

    initEventListeners() {
        // JSON格式实时验证
        const caseDataTextarea = document.getElementById('caseData');
        if (caseDataTextarea) {
            caseDataTextarea.addEventListener('input', this.validateJSON.bind(this));
        }

        // 表单提交
        const testCaseForm = document.getElementById('testCaseForm');
        if (testCaseForm) {
            testCaseForm.addEventListener('submit', this.handleSubmit.bind(this));
        }

        // 格式化JSON按钮
        const formatBtn = document.getElementById('formatJSON');
        if (formatBtn) {
            formatBtn.addEventListener('click', this.formatJSON.bind(this));
        }
    }

    validateJSON(event) {
        const textarea = event.target;
        const value = textarea.value.trim();

        if (value === '') {
            this.clearValidation();
            return;
        }

        if (TestPlatformUtils.isValidJSON(value)) {
            this.showValidationState('valid', 'JSON格式正确');
        } else {
            this.showValidationState('invalid', 'JSON格式错误');
        }
    }

    clearValidation() {
        const textarea = document.getElementById('caseData');
        const hint = document.querySelector('.json-validation-hint');

        if (textarea) {
            textarea.classList.remove('valid', 'invalid');
        }
        if (hint) {
            hint.remove();
        }
    }

    showValidationState(state, message) {
        const textarea = document.getElementById('caseData');
        let hint = document.querySelector('.json-validation-hint');

        // 移除现有状态类
        textarea.classList.remove('valid', 'invalid');
        textarea.classList.add(state);

        // 创建或更新提示信息
        if (!hint) {
            hint = document.createElement('div');
            hint.className = 'json-validation-hint';
            textarea.parentNode.appendChild(hint);
        }

        hint.textContent = message;
        hint.className = `json-validation-hint ${state}`;
    }

    formatJSON() {
        const textarea = document.getElementById('caseData');
        if (textarea) {
            textarea.value = TestPlatformUtils.formatJSON(textarea.value);
        }
    }

    async handleSubmit(event) {
        event.preventDefault();

        const caseName = document.getElementById('caseName').value.trim();
        const caseData = document.getElementById('caseData').value.trim();

        if (!caseName) {
            TestPlatformUtils.showMessage('请输入用例名称', 'error');
            return;
        }

        if (!caseData) {
            TestPlatformUtils.showMessage('请输入用例数据', 'error');
            return;
        }

        if (!TestPlatformUtils.isValidJSON(caseData)) {
            TestPlatformUtils.showMessage('用例数据必须是有效的JSON格式', 'error');
            return;
        }

        try {
            const response = await fetch('/api/test-cases', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    case_name: caseName,
                    case_data: caseData
                })
            });

            const result = await response.json();

            if (result.success) {
                TestPlatformUtils.showMessage(result.message, 'success');
                // 清空表单
                document.getElementById('testCaseForm').reset();
                this.clearValidation();
                // 刷新页面显示新用例
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                TestPlatformUtils.showMessage(result.message, 'error');
            }
        } catch (error) {
            console.error('保存测试用例失败:', error);
            TestPlatformUtils.showMessage('保存失败，请检查网络连接', 'error');
        }
    }
}

// 测试执行相关功能
class TestExecutor {
    constructor() {
        this.initEventListeners();
    }

    initEventListeners() {
        const executeBtn = document.getElementById('executeBtn');
        if (executeBtn) {
            executeBtn.addEventListener('click', this.executeTests.bind(this));
        }

        const stopBtn = document.getElementById('stopBtn');
        if (stopBtn) {
            stopBtn.addEventListener('click', this.stopTests.bind(this));
        }

        const downloadBtn = document.getElementById('downloadReport');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', this.downloadReport.bind(this));
        }
    }

    async executeTests() {
        const mark = document.getElementById('testMark').value;
        const logOutput = document.getElementById('logOutput');
        const executeBtn = document.getElementById('executeBtn');

        // 禁用执行按钮
        executeBtn.disabled = true;
        executeBtn.textContent = '执行中...';

        // 清空日志
        logOutput.innerHTML = '<div class="log-entry">开始执行测试... ' + new Date().toLocaleString() + '</div>';

        try {
            const response = await fetch('/api/execute-tests', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mark: mark
                })
            });

            const result = await response.json();

            if (result.success) {
                logOutput.innerHTML += `<div class="log-entry success">${result.message}</div>`;
                logOutput.innerHTML += `<div class="log-entry">测试正在后台执行，请查看控制台输出或报告文件。</div>`;

                // 轮询获取执行状态
                this.pollExecutionStatus();
            } else {
                logOutput.innerHTML += `<div class="log-entry error">${result.message}</div>`;
            }
        } catch (error) {
            console.error('执行测试失败:', error);
            logOutput.innerHTML += `<div class="log-entry error">执行失败: ${error.message}</div>`;
        } finally {
            // 重新启用执行按钮
            setTimeout(() => {
                executeBtn.disabled = false;
                executeBtn.textContent = '开始执行测试';
            }, 5000);
        }
    }

    async pollExecutionStatus() {
        // 这里可以实现轮询获取测试执行状态的功能
        // 由于测试执行是异步的，可以通过WebSocket或定期请求来获取状态更新
        console.log('开始轮询测试执行状态...');
    }

    stopTests() {
        // 停止测试执行
        fetch('/api/stop-tests', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                TestPlatformUtils.showMessage('测试已停止', 'success');
            } else {
                TestPlatformUtils.showMessage('停止测试失败', 'error');
            }
        })
        .catch(error => {
            console.error('停止测试失败:', error);
            TestPlatformUtils.showMessage('停止测试失败', 'error');
        });
    }

    downloadReport() {
        const reportType = document.getElementById('reportType').value;
        TestPlatformUtils.downloadReport(`${reportType}_report.html`);
    }
}

// Mock服务管理
class MockManager {
    constructor() {
        this.initEventListeners();
    }

    initEventListeners() {
        const testMockBtn = document.getElementById('testMockBtn');
        if (testMockBtn) {
            testMockBtn.addEventListener('click', this.testMockAPI.bind(this));
        }

        const mockUrlInputs = document.querySelectorAll('.mock-url');
        mockUrlInputs.forEach(input => {
            input.addEventListener('click', this.copyMockURL.bind(this));
        });
    }

    async testMockAPI() {
        const apiSelect = document.getElementById('mockApiSelect');
        const resultDiv = document.getElementById('mockTestResult');

        const selectedApi = apiSelect.value;
        let url = '';
        let method = 'GET';
        let body = null;

        switch (selectedApi) {
            case 'get_users':
                url = '/mock/api/users';
                method = 'GET';
                break;
            case 'get_user':
                url = '/mock/api/users/1';
                method = 'GET';
                break;
            case 'create_user':
                url = '/mock/api/users';
                method = 'POST';
                body = JSON.stringify({
                    name: '测试用户',
                    email: 'test@example.com',
                    age: 25,
                    department: '测试部'
                });
                break;
            case 'calculator_add':
                url = '/mock/api/calculator/add';
                method = 'POST';
                body = JSON.stringify({
                    a: 10,
                    b: 5
                });
                break;
        }

        try {
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            if (body) {
                options.body = body;
            }

            const response = await fetch(url, options);
            const data = await response.json();

            resultDiv.innerHTML = `
                <div class="mock-result">
                    <h4>请求:</h4>
                    <pre>${method} ${url}${body ? '\n' + body : ''}</pre>
                    <h4>响应:</h4>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                </div>
            `;

        } catch (error) {
            resultDiv.innerHTML = `
                <div class="mock-result error">
                    <h4>请求失败:</h4>
                    <pre>${error.message}</pre>
                </div>
            `;
        }
    }

    copyMockURL(event) {
        const url = event.target.textContent || event.target.value;
        navigator.clipboard.writeText(url).then(() => {
            TestPlatformUtils.showMessage('URL已复制到剪贴板', 'success');
        }).catch(err => {
            console.error('复制失败:', err);
            TestPlatformUtils.showMessage('复制失败', 'error');
        });
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 根据当前页面初始化相应的功能模块
    const path = window.location.pathname;

    if (path.includes('test-cases')) {
        new TestCaseManager();
    } else if (path.includes('test-execution')) {
        new TestExecutor();
    } else if (path.includes('mock-management')) {
        new MockManager();
    }

    // 添加CSS动画
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }

        .json-validation-hint {
            margin-top: 5px;
            font-size: 12px;
            padding: 4px 8px;
            border-radius: 3px;
        }

        .json-validation-hint.valid {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .json-validation-hint.invalid {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        textarea.valid {
            border-color: #28a745;
        }

        textarea.invalid {
            border-color: #dc3545;
        }

        .log-entry {
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }

        .log-entry.success {
            color: #28a745;
        }

        .log-entry.error {
            color: #dc3545;
        }

        .log-entry.warning {
            color: #ffc107;
        }

        .mock-result {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 15px;
            margin-top: 10px;
        }

        .mock-result pre {
            background: white;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
        }

        .mock-result.error {
            border-color: #dc3545;
            background: #f8d7da;
        }
    `;
    document.head.appendChild(style);
});

// 全局错误处理
window.addEventListener('error', function(e) {
    console.error('全局错误:', e.error);
    TestPlatformUtils.showMessage('发生未知错误，请查看控制台', 'error');
});

// 导出到全局作用域
window.TestPlatformUtils = TestPlatformUtils;
window.TestCaseManager = TestCaseManager;
window.TestExecutor = TestExecutor;
window.MockManager = MockManager;