// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    console.log('Loading charts...');

    // Fetch data from API
    fetch('/api/chart-data/')
        .then(response => {
            if (!response.ok) throw new Error('API error');
            return response.json();
        })
        .then(data => {
            console.log('Chart data:', data);

            // 1. Health Chart
            const healthCanvas = document.getElementById('healthChart');
            if (healthCanvas && data.health) {
                new Chart(healthCanvas, {
                    type: 'doughnut',
                    data: {
                        datasets: [{
                            data: [data.health.score, 100 - data.health.score],
                            backgroundColor: [data.health.color, 'rgba(255,255,255,0.1)'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        cutout: '75%',
                        plugins: {
                            legend: { display: false },
                            tooltip: { enabled: false }
                        }
                    }
                });
                console.log('✓ Health chart created');
            }

            // 2. Expense Breakdown
            const expenseCanvas = document.getElementById('expenseBreakdownChart');
            if (expenseCanvas && data.gastos_por_categoria && data.gastos_por_categoria.length > 0) {
                new Chart(expenseCanvas, {
                    type: 'doughnut',
                    data: {
                        labels: data.gastos_por_categoria.map(c => c.nombre),
                        datasets: [{
                            data: data.gastos_por_categoria.map(c => c.total),
                            backgroundColor: data.gastos_por_categoria.map(c => c.color)
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: { color: '#94a3b8' }
                            }
                        }
                    }
                });
                console.log('✓ Expense chart created');
            }

            // 3. Monthly Trend
            const trendCanvas = document.getElementById('monthlyTrendChart');
            if (trendCanvas && data.monthly && data.monthly.labels.length > 0) {
                new Chart(trendCanvas, {
                    type: 'line',
                    data: {
                        labels: data.monthly.labels,
                        datasets: [{
                            label: 'Ingresos',
                            data: data.monthly.ingresos,
                            borderColor: '#10b981',
                            fill: false
                        }, {
                            label: 'Gastos',
                            data: data.monthly.gastos,
                            borderColor: '#ef4444',
                            fill: false
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { labels: { color: '#94a3b8' } }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { color: '#94a3b8' }
                            },
                            x: { ticks: { color: '#94a3b8' } }
                        }
                    }
                });
                console.log('✓ Trend chart created');
            }
        })
        .catch(error => console.error('Chart error:', error));
});
