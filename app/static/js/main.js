// 通用工具函数
const utils = {
    // 格式化数字
    formatNumber: function(num) {
        return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
    },

    // 格式化金额
    formatCurrency: function(num) {
        return '¥ ' + this.formatNumber(parseFloat(num).toFixed(2));
    },

    // 格式化日期时间
    formatDateTime: function(date) {
        const d = new Date(date);
        const pad = (n) => n < 10 ? '0' + n : n;
        return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
    },

    // 显示加载动画
    showLoading: function(element) {
        element.classList.add('loading');
    },

    // 隐藏加载动画
    hideLoading: function(element) {
        element.classList.remove('loading');
    },

    // 显示提示消息
    showToast: function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            document.body.removeChild(toast);
        });
    }
};

// 表单验证
const formValidation = {
    // 验证必填字段
    required: function(value) {
        return value !== null && value.trim() !== '';
    },

    // 验证邮箱格式
    email: function(value) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    },

    // 验证手机号格式
    phone: function(value) {
        return /^1[3-9]\d{9}$/.test(value);
    },

    // 验证数字
    number: function(value) {
        return !isNaN(parseFloat(value)) && isFinite(value);
    },

    // 验证整数
    integer: function(value) {
        return Number.isInteger(Number(value));
    },

    // 验证正数
    positive: function(value) {
        return this.number(value) && parseFloat(value) > 0;
    }
};

// 图表配置
const chartConfig = {
    // 通用配置
    common: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1000,
            easing: 'easeOutQuart'
        },
        plugins: {
            legend: {
                position: 'top'
            },
            tooltip: {
                mode: 'index',
                intersect: false
            }
        }
    },

    // 颜色方案
    colors: {
        primary: '#0d6efd',
        success: '#198754',
        info: '#0dcaf0',
        warning: '#ffc107',
        danger: '#dc3545',
        secondary: '#6c757d'
    },

    // 渐变背景
    getGradient: function(ctx, color) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, color + '80');
        gradient.addColorStop(1, color + '10');
        return gradient;
    }
};

// 数据表格功能
const dataTable = {
    // 初始化排序
    initSort: function(table) {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const column = header.dataset.sort;
                const direction = header.classList.contains('asc') ? 'desc' : 'asc';
                
                // 清除其他列的排序状态
                headers.forEach(h => h.classList.remove('asc', 'desc'));
                header.classList.add(direction);
                
                this.sortTable(table, column, direction);
            });
        });
    },

    // 表格排序
    sortTable: function(table, column, direction) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aValue = a.querySelector(`td[data-${column}]`).dataset[column];
            const bValue = b.querySelector(`td[data-${column}]`).dataset[column];
            
            if (direction === 'asc') {
                return aValue.localeCompare(bValue, undefined, {numeric: true});
            } else {
                return bValue.localeCompare(aValue, undefined, {numeric: true});
            }
        });
        
        rows.forEach(row => tbody.appendChild(row));
    },

    // 初始化搜索
    initSearch: function(input, table) {
        input.addEventListener('input', () => {
            const searchText = input.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchText) ? '' : 'none';
            });
        });
    }
};

// 文件上传功能
const fileUpload = {
    // 验证文件类型
    validateType: function(file, allowedTypes) {
        return allowedTypes.includes(file.type);
    },

    // 验证文件大小
    validateSize: function(file, maxSize) {
        return file.size <= maxSize;
    },

    // 格式化文件大小
    formatSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
};

// 页面加载完成后执行
$(document).ready(function() {
    // 初始化所有工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 初始化所有弹出框
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // 自动隐藏警告消息
    $('.alert').not('.alert-permanent').delay(5000).fadeOut(500);

    // 添加表单验证
    $('form').on('submit', function() {
        var isValid = true;
        $(this).find('input[required], select[required], textarea[required]').each(function() {
            if (!$(this).val()) {
                isValid = false;
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        return isValid;
    });

    // 输入框验证状态实时更新
    $('input[required], select[required], textarea[required]').on('input change', function() {
        if ($(this).val()) {
            $(this).removeClass('is-invalid');
        }
    });

    // 移动端导航栏自动收起
    $('.navbar-nav>li>a').on('click', function(){
        $('.navbar-collapse').collapse('hide');
    });

    // 文件上传预览
    $('input[type="file"]').on('change', function() {
        var fileName = $(this).val().split('\\').pop();
        $(this).next('.custom-file-label').html(fileName);
    });
}); 