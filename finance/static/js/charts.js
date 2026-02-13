/**
 * WALLET FLOW - Chart Configurations
 * Enhanced Chart.js configurations with animations
 */

// ============================================
// CHART DEFAULTS
// ============================================
const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: '#cbd5e1',
                font: {
                    family: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                    size: 12
                },
                padding: 15,
                usePointStyle: true
            }
        },
        tooltip: {
            backgroundColor: 'rgba(30, 41, 59, 0.95)',
            titleColor: '#f1f5f9',
            bodyColor: '#cbd5e1',
            borderColor: '#334155',
            borderWidth: 1,
            padding: 12,
            cornerRadius: 8,
            displayColors: true,
            callbacks: {
                label: function (context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    label += '$' + context.parsed.y.toLocaleString();
                    return label;
                }
            }
        }
    },
    animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
    }
};

// ============================================
// FINANCIAL HEALTH DOUGHNUT CHART
// ============================================
function createHealthChart(canvasId, percentage) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const color = percentage >= 70 ? '#10b981' : percentage >= 40 ? '#f59e0b' : '#ef4444';

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Salud', 'Restante'],
            datasets: [{
                data: [percentage, 100 - percentage],
                backgroundColor: [color, '#1e293b'],
                borderWidth: 0,
                cutout: '75%'
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                ...chartDefaults.plugins,
                legend: { display: false },
                tooltip: { enabled: false }
            }
        }
    });
}

// ============================================
// INCOME VS EXPENSES BAR CHART
// ============================================
function createIncomeExpensesChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Ingresos',
                    data: data.income,
                    backgroundColor: 'rgba(99, 102, 241, 0.8)',
                    borderColor: '#6366f1',
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false
                },
                {
                    label: 'Gastos',
                    data: data.expenses,
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    borderColor: '#ef4444',
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false
                }
            ]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#334155',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        callback: function (value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                }
            }
        }
    });
}

// ============================================
// SPENDING BY CATEGORY PIE CHART
// ============================================
function createCategoryChart(canvasId, categories, amounts) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const colors = [
        '#6366f1', '#8b5cf6', '#ec4899', '#f59e0b',
        '#10b981', '#3b82f6', '#ef4444', '#14b8a6'
    ];

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categories,
            datasets: [{
                data: amounts,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#1e293b',
                hoverOffset: 10
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                ...chartDefaults.plugins,
                legend: {
                    ...chartDefaults.plugins.legend,
                    position: 'right'
                }
            }
        }
    });
}

// ============================================
// TREND LINE CHART
// ============================================
function createTrendChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Balance',
                data: data,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: '#334155',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        callback: function (value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        color: '#334155',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                }
            }
        }
    });
}

// ============================================
// PROGRESS CHART (for goals)
// ============================================
function createProgressChart(canvasId, current, target) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const percentage = Math.min((current / target) * 100, 100);
    const color = percentage >= 100 ? '#10b981' : percentage >= 50 ? '#6366f1' : '#f59e0b';

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [current, Math.max(target - current, 0)],
                backgroundColor: [color, '#1e293b'],
                borderWidth: 0,
                cutout: '70%'
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                ...chartDefaults.plugins,
                legend: { display: false },
                tooltip: {
                    ...chartDefaults.plugins.tooltip,
                    callbacks: {
                        label: function (context) {
                            return context.parsed + '%';
                        }
                    }
                }
            }
        }
    });
}

// ============================================
// UPDATE CHART DATA
// ============================================
function updateChartData(chart, newData) {
    if (!chart) return;

    chart.data.datasets.forEach((dataset, i) => {
        dataset.data = newData[i];
    });

    chart.update('active');
}

// Export for global use
window.ChartUtils = {
    createHealthChart,
    createIncomeExpensesChart,
    createCategoryChart,
    createTrendChart,
    createProgressChart,
    updateChartData
};
