// 全局变量
let entries = [];
let filteredEntries = [];

// DOM 元素
const entriesContainer = document.getElementById('entries-container');
const loadingElement = document.getElementById('loading');
const noEntriesElement = document.getElementById('no-entries');
const searchInput = document.getElementById('search-input');
const refreshBtn = document.getElementById('refresh-btn');
const addForm = document.getElementById('add-form');
const confirmModal = document.getElementById('confirm-modal');
const confirmMessage = document.getElementById('confirm-message');
const confirmCancelBtn = document.getElementById('confirm-cancel');
const confirmOkBtn = document.getElementById('confirm-ok');

// 统计元素
const totalIpsElement = document.getElementById('total-ips');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    loadEntries();
    setupEventListeners();
});

// 设置事件监听器
function setupEventListeners() {
    // 搜索功能
    searchInput.addEventListener('input', function() {
        filterEntries();
    });

    // 刷新按钮
    refreshBtn.addEventListener('click', function() {
        loadEntries();
        showToast('正在刷新...', 'info');
    });

    // 添加表单
    addForm.addEventListener('submit', function(e) {
        e.preventDefault();
        handleAddEntry();
    });

    // 模态框事件
    confirmCancelBtn.addEventListener('click', closeModal);
    confirmOkBtn.addEventListener('click', confirmAction);

    // 点击模态框外部关闭
    confirmModal.addEventListener('click', function(e) {
        if (e.target === confirmModal) {
            closeModal();
        }
    });

    // ESC 键关闭模态框
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && confirmModal.style.display === 'block') {
            closeModal();
        }
    });
}

// 加载条目
async function loadEntries() {
    showLoading(true);

    try {
        const response = await fetch('/api/entries');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        entries = await response.json();
        filteredEntries = [...entries];

        updateStatistics();
        renderEntries();

        if (entries.length === 0) {
            showNoEntries(true);
        } else {
            showNoEntries(false);
        }
    } catch (error) {
        console.error('加载条目失败:', error);
        showToast('加载条目失败: ' + error.message, 'error');
        showNoEntries(true);
    } finally {
        showLoading(false);
    }
}

// 渲染条目列表
function renderEntries() {
    entriesContainer.innerHTML = '';

    if (filteredEntries.length === 0) {
        showNoEntries(true);
        return;
    }

    showNoEntries(false);

    filteredEntries.forEach((entry, index) => {
        const entryElement = createEntryElement(entry, index);
        entriesContainer.appendChild(entryElement);
    });
}

// 创建条目元素
function createEntryElement(entry, index) {
    const div = document.createElement('div');
    div.className = 'entry-item';
    div.dataset.index = index;

    div.innerHTML = `
        <div class="entry-info">
            <div class="entry-ip">
                <i class="fas fa-network-wired"></i>
                ${escapeHtml(entry.ip)}
            </div>
        </div>
        <div class="entry-actions">
            <button class="btn btn-danger btn-sm" onclick="confirmRemoveEntry('${escapeHtml(entry.ip)}')">
                <i class="fas fa-trash"></i>
                删除
            </button>
        </div>
    `;

    return div;
}

// 更新统计信息
function updateStatistics() {
    // 总 IP 数
    totalIpsElement.textContent = entries.length;
}

// 筛选条目
function filterEntries() {
    const searchTerm = searchInput.value.toLowerCase().trim();

    if (searchTerm === '') {
        filteredEntries = [...entries];
    } else {
        filteredEntries = entries.filter(entry =>
            entry.ip.toLowerCase().includes(searchTerm)
        );
    }

    renderEntries();
}

// 处理添加条目
async function handleAddEntry() {
    const ipInput = document.getElementById('ip');

    const ip = ipInput.value.trim();

    if (!ip) {
        showToast('请填写 IP 地址', 'warning');
        return;
    }

    // 验证 IP 格式
    if (!isValidIP(ip)) {
        showToast('请输入有效的 IP 地址', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ip: ip
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast(result.message, 'success');
            ipInput.value = '';
            loadEntries();
        } else {
            showToast(result.message, 'error');
        }
    } catch (error) {
        console.error('添加 IP 失败:', error);
        showToast('添加失败: ' + error.message, 'error');
    }
}

// 确认删除条目
function confirmRemoveEntry(ip) {
    confirmMessage.textContent = `确定要删除 IP 地址 "${ip}" 吗？此操作不可恢复。`;
    confirmModal.style.display = 'block';
    confirmModal.dataset.action = 'remove';
    confirmModal.dataset.ip = ip;
}

// 确认操作
async function confirmAction() {
    const action = confirmModal.dataset.action;
    const ip = confirmModal.dataset.ip;

    closeModal();

    if (action === 'remove') {
        await removeEntry(ip);
    }
}

// 删除条目
async function removeEntry(ip) {
    try {
        const response = await fetch('/api/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ip: ip
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast(result.message, 'success');
            loadEntries();
        } else {
            showToast(result.message, 'error');
        }
    } catch (error) {
        console.error('删除 IP 失败:', error);
        showToast('删除失败: ' + error.message, 'error');
    }
}

// 关闭模态框
function closeModal() {
    confirmModal.style.display = 'none';
    delete confirmModal.dataset.action;
    delete confirmModal.dataset.ip;
}

// 显示加载状态
function showLoading(show) {
    loadingElement.style.display = show ? 'block' : 'none';
    if (show) {
        entriesContainer.style.display = 'none';
        noEntriesElement.style.display = 'none';
    }
}

// 显示无条目状态
function showNoEntries(show) {
    noEntriesElement.style.display = show ? 'block' : 'none';
    entriesContainer.style.display = show ? 'none' : 'block';
}

// 显示 Toast 消息
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icon = getToastIcon(type);
    toast.innerHTML = `<i class="fas ${icon}"></i> ${message}`;

    toastContainer.appendChild(toast);

    // 自动移除 Toast
    setTimeout(() => {
        toast.style.animation = 'toastSlideIn 0.3s ease reverse';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// 获取 Toast 图标
function getToastIcon(type) {
    const icons = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };
    return icons[type] || 'fa-info-circle';
}

// 验证 IP 地址
function isValidIP(ip) {
    // IPv4 正则表达式
    const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

    // IPv6 正则表达式（简化版）
    const ipv6Regex = /^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/;

    return ipv4Regex.test(ip) || ipv6Regex.test(ip);
}

// 验证主机名
function isValidHostname(hostname) {
    if (!hostname || hostname.length > 253) {
        return false;
    }

    // 主机名正则表达式
    const hostnameRegex = /^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$/;
    return hostnameRegex.test(hostname);
}

// HTML 转义
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 应用防抖到搜索功能
searchInput.addEventListener('input', debounce(function() {
    filterEntries();
}, 300));