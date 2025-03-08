// 图表主题配置
const chartTheme = {
    colors: [
        '#0d6efd', '#198754', '#0dcaf0', '#ffc107', '#dc3545',
        '#6610f2', '#6f42c1', '#d63384', '#fd7e14', '#20c997'
    ],
    font: {
        family: '"Microsoft YaHei", -apple-system, sans-serif'
    },
    background: '#ffffff',
    grid: {
        color: '#e9ecef'
    }
};

// 图表工具类
const chartUtils = {
    // 创建渐变色
    createGradient: function(color) {
        return [
            [0, color + 'FF'],
            [0.5, color + '99'],
            [1, color + '33']
        ];
    },

    // 格式化数字
    formatNumber: function(num) {
        return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
    },

    // 格式化金额
    formatCurrency: function(num) {
        return '¥ ' + this.formatNumber(parseFloat(num).toFixed(2));
    }
};

// 图表配置生成器
const chartConfigs = {
    // 区域房价分布图配置
    districtPrice: function(data) {
        return {
            bar: {
                x: data.districts,
                y: data.avg_prices,
                name: '平均总价(万元)',
                type: 'bar',
                marker: {
                    color: chartTheme.colors[0]
                }
            },
            line: {
                x: data.districts,
                y: data.avg_unit_prices,
                name: '平均单价(元/㎡)',
                type: 'scatter',
                yaxis: 'y2',
                marker: {
                    color: chartTheme.colors[1]
                }
            },
            layout: {
                title: '各区域房价分布',
                showlegend: true,
                yaxis: {title: '平均总价(万元)'},
                yaxis2: {
                    title: '平均单价(元/㎡)',
                    overlaying: 'y',
                    side: 'right'
                },
                hovermode: 'closest'
            }
        };
    },

    // 户型分布图配置
    houseType: function(data) {
        return {
            data: [{
                labels: data.types,
                values: data.counts,
                type: 'pie',
                hole: 0.4,
                textinfo: 'label+percent',
                textposition: 'outside',
                marker: {
                    colors: chartTheme.colors
                }
            }],
            layout: {
                title: '户型分布情况',
                showlegend: true,
                legend: {
                    orientation: 'h',
                    y: -0.2
                }
            }
        };
    },

    // 价格区间分布图配置
    priceDistribution: function(data) {
        return {
            data: [{
                x: data.ranges,
                y: data.counts,
                type: 'bar',
                marker: {
                    color: chartTheme.colors[2],
                    opacity: 0.6,
                    line: {
                        color: chartTheme.colors[0],
                        width: 1.5
                    }
                }
            }],
            layout: {
                title: '价格区间分布',
                xaxis: {title: '价格区间(万元)'},
                yaxis: {title: '房源数量'},
                bargap: 0.1
            }
        };
    },

    // 面积价格散点图配置
    areaPrice: function(data) {
        return {
            data: [{
                x: data.scatter_data.areas,
                y: data.scatter_data.prices,
                mode: 'markers',
                type: 'scatter',
                marker: {
                    size: 8,
                    color: data.scatter_data.unit_prices,
                    colorscale: 'Viridis',
                    showscale: true,
                    colorbar: {title: '单价(元/㎡)'}
                }
            }],
            layout: {
                title: '面积与总价关系',
                xaxis: {title: '面积(㎡)'},
                yaxis: {title: '总价(万元)'},
                hovermode: 'closest'
            }
        };
    },

    // 年度统计图配置
    yearlyStats: function(data) {
        return {
            data: [{
                x: data.years,
                y: data.avg_prices,
                name: '平均总价(万元)',
                type: 'scatter',
                mode: 'lines+markers',
                marker: {color: chartTheme.colors[0]}
            }, {
                x: data.years,
                y: data.counts,
                name: '房源数量',
                type: 'bar',
                yaxis: 'y2',
                marker: {color: chartTheme.colors[1]}
            }],
            layout: {
                title: '建筑年代与房价关系',
                xaxis: {title: '建筑年代'},
                yaxis: {title: '平均总价(万元)'},
                yaxis2: {
                    title: '房源数量',
                    overlaying: 'y',
                    side: 'right'
                },
                showlegend: true
            }
        };
    }
};

// 图表管理器
class ChartManager {
    constructor() {
        this.charts = new Map();
        this.init();
    }

    init() {
        // 设置Plotly主题
        const template = {
            layout: {
                font: chartTheme.font,
                paper_bgcolor: chartTheme.background,
                plot_bgcolor: chartTheme.background,
                xaxis: {
                    gridcolor: chartTheme.grid.color,
                    zerolinecolor: chartTheme.grid.color
                },
                yaxis: {
                    gridcolor: chartTheme.grid.color,
                    zerolinecolor: chartTheme.grid.color
                }
            }
        };
        Plotly.setPlotConfig({template: template});

        // 初始化所有图表
        this.initDistrictPriceChart();
        this.initHouseTypeChart();
        this.initPriceDistributionChart();
        this.initAreaPriceChart();
        this.initYearlyStatsChart();

        // 监听窗口大小变化
        window.addEventListener('resize', () => this.handleResize());
    }

    // 初始化区域房价分布图
    initDistrictPriceChart() {
        const container = document.getElementById('districtPriceChart');
        if (!container) return;

        utils.showLoading(container);
        fetch('/api/stats/district')
            .then(response => response.json())
            .then(data => {
                const config = chartConfigs.districtPrice(data);
                Plotly.newPlot(container, [config.bar, config.line], config.layout);
                this.charts.set('districtPrice', container);
            })
            .finally(() => utils.hideLoading(container));
    }

    // 初始化户型分布图
    initHouseTypeChart() {
        const container = document.getElementById('houseTypeChart');
        if (!container) return;

        utils.showLoading(container);
        fetch('/api/stats/house_type')
            .then(response => response.json())
            .then(data => {
                const config = chartConfigs.houseType(data);
                Plotly.newPlot(container, config.data, config.layout);
                this.charts.set('houseType', container);
            })
            .finally(() => utils.hideLoading(container));
    }

    // 初始化价格区间分布图
    initPriceDistributionChart() {
        const container = document.getElementById('priceDistributionChart');
        if (!container) return;

        utils.showLoading(container);
        fetch('/api/stats/price_distribution')
            .then(response => response.json())
            .then(data => {
                const config = chartConfigs.priceDistribution(data);
                Plotly.newPlot(container, config.data, config.layout);
                this.charts.set('priceDistribution', container);
            })
            .finally(() => utils.hideLoading(container));
    }

    // 初始化面积价格散点图
    initAreaPriceChart() {
        const container = document.getElementById('areaPriceChart');
        if (!container) return;

        utils.showLoading(container);
        fetch('/api/stats/area_price')
            .then(response => response.json())
            .then(data => {
                const config = chartConfigs.areaPrice(data);
                Plotly.newPlot(container, config.data, config.layout);
                this.charts.set('areaPrice', container);
            })
            .finally(() => utils.hideLoading(container));
    }

    // 初始化年度统计图
    initYearlyStatsChart() {
        const container = document.getElementById('yearlyStatsChart');
        if (!container) return;

        utils.showLoading(container);
        fetch('/api/stats/yearly')
            .then(response => response.json())
            .then(data => {
                const config = chartConfigs.yearlyStats(data);
                Plotly.newPlot(container, config.data, config.layout);
                this.charts.set('yearlyStats', container);
            })
            .finally(() => utils.hideLoading(container));
    }

    // 处理窗口大小变化
    handleResize() {
        this.charts.forEach(container => {
            Plotly.relayout(container, {
                'xaxis.automargin': true,
                'yaxis.automargin': true
            });
        });
    }
}

// 页面加载完成后初始化图表
document.addEventListener('DOMContentLoaded', () => {
    new ChartManager();
});