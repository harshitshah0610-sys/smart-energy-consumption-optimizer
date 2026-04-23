/**
 * Smart Energy Consumption Optimizer — Chart Module
 * Creates interactive Chart.js visualizations for the dashboard.
 */

// Store chart instances for cleanup
const chartInstances = {};

/**
 * Get theme-aware colors for charts
 */
function getChartColors() {
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    return {
        text: isDark ? '#94a3b8' : '#475569',
        grid: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
        tooltipBg: isDark ? '#1e293b' : '#ffffff',
        tooltipText: isDark ? '#f1f5f9' : '#0f172a',
        palette: [
            '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6',
            '#f43f5e', '#06b6d4', '#84cc16', '#ec4899',
            '#14b8a6', '#6366f1'
        ]
    };
}

/**
 * Destroy an existing chart before recreating
 */
function destroyChart(chartId) {
    if (chartInstances[chartId]) {
        chartInstances[chartId].destroy();
        delete chartInstances[chartId];
    }
}

/**
 * Create Doughnut chart — Energy breakdown by appliance
 */
function createBreakdownChart(canvasId, appliances) {
    destroyChart(canvasId);
    const colors = getChartColors();
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = appliances.map(a => a.name);
    const data = appliances.map(a => a.daily_kwh);

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.palette.slice(0, labels.length),
                borderWidth: 0,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: colors.text,
                        font: { family: "'Inter', sans-serif", size: 12 },
                        padding: 16,
                        usePointStyle: true,
                        pointStyleWidth: 10
                    }
                },
                tooltip: {
                    backgroundColor: colors.tooltipBg,
                    titleColor: colors.tooltipText,
                    bodyColor: colors.tooltipText,
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    titleFont: { family: "'Inter', sans-serif", weight: '600' },
                    bodyFont: { family: "'Inter', sans-serif" },
                    callbacks: {
                        label: function (ctx) {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((ctx.parsed / total) * 100).toFixed(1);
                            return ` ${ctx.label}: ${ctx.parsed} kWh (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create Bar chart — Before vs After optimization comparison
 */
function createComparisonChart(canvasId, optimizedAppliances) {
    destroyChart(canvasId);
    const colors = getChartColors();
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Filter to top 8 appliances by energy usage
    const sorted = [...optimizedAppliances]
        .sort((a, b) => b.original_kwh - a.original_kwh)
        .slice(0, 8);

    const labels = sorted.map(a => a.name);
    const originalData = sorted.map(a => a.original_kwh);
    const optimizedData = sorted.map(a => a.optimized_kwh);

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Current Usage',
                    data: originalData,
                    backgroundColor: 'rgba(239, 68, 68, 0.7)',
                    borderColor: '#ef4444',
                    borderWidth: 1,
                    borderRadius: 6,
                    borderSkipped: false
                },
                {
                    label: 'Optimized Usage',
                    data: optimizedData,
                    backgroundColor: 'rgba(16, 185, 129, 0.7)',
                    borderColor: '#10b981',
                    borderWidth: 1,
                    borderRadius: 6,
                    borderSkipped: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        color: colors.text,
                        font: { family: "'Inter', sans-serif", size: 11 }
                    }
                },
                y: {
                    grid: { color: colors.grid },
                    ticks: {
                        color: colors.text,
                        font: { family: "'Inter', sans-serif", size: 11 },
                        callback: v => v + ' kWh'
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: colors.text,
                        font: { family: "'Inter', sans-serif", size: 12 },
                        usePointStyle: true,
                        pointStyleWidth: 10
                    }
                },
                tooltip: {
                    backgroundColor: colors.tooltipBg,
                    titleColor: colors.tooltipText,
                    bodyColor: colors.tooltipText,
                    cornerRadius: 8,
                    padding: 12,
                    titleFont: { family: "'Inter', sans-serif", weight: '600' },
                    bodyFont: { family: "'Inter', sans-serif" },
                }
            }
        }
    });
}

/**
 * Create Line chart — Weekly usage trend simulation
 */
function createTrendChart(canvasId, dailyKwh) {
    destroyChart(canvasId);
    const colors = getChartColors();
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

    // Simulate weekly variation (±20%)
    const weekdayMultipliers = [0.95, 1.0, 0.98, 1.02, 1.05, 1.2, 1.15];
    const currentData = weekdayMultipliers.map(m =>
        parseFloat((dailyKwh * m * (0.9 + Math.random() * 0.2)).toFixed(2))
    );
    const optimizedData = currentData.map(v =>
        parseFloat((v * 0.78).toFixed(2))
    );

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: days,
            datasets: [
                {
                    label: 'Current Usage',
                    data: currentData,
                    borderColor: '#f43f5e',
                    backgroundColor: 'rgba(244, 63, 94, 0.08)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    pointBackgroundColor: '#f43f5e',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    borderWidth: 2.5
                },
                {
                    label: 'Optimized Usage',
                    data: optimizedData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.08)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    borderWidth: 2.5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        color: colors.text,
                        font: { family: "'Inter', sans-serif", size: 12 }
                    }
                },
                y: {
                    grid: { color: colors.grid },
                    ticks: {
                        color: colors.text,
                        font: { family: "'Inter', sans-serif", size: 11 },
                        callback: v => v + ' kWh'
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: colors.text,
                        font: { family: "'Inter', sans-serif", size: 12 },
                        usePointStyle: true,
                        pointStyleWidth: 10
                    }
                },
                tooltip: {
                    backgroundColor: colors.tooltipBg,
                    titleColor: colors.tooltipText,
                    bodyColor: colors.tooltipText,
                    cornerRadius: 8,
                    padding: 12,
                    titleFont: { family: "'Inter', sans-serif", weight: '600' },
                    bodyFont: { family: "'Inter', sans-serif" },
                }
            }
        }
    });
}

/**
 * Create Scenario comparison bar chart
 */
function createScenarioChart(canvasId, simulationData) {
    destroyChart(canvasId);
    const colors = getChartColors();
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = Object.keys(simulationData).map(k =>
        k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    );
    const data = Object.values(simulationData).map(v => v.daily_kwh);

    const bgColors = data.map((v, i) => {
        if (i === 0) return 'rgba(59, 130, 246, 0.7)'; // Current
        return v > data[0]
            ? 'rgba(239, 68, 68, 0.7)'
            : 'rgba(16, 185, 129, 0.7)';
    });

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Daily Usage (kWh)',
                data: data,
                backgroundColor: bgColors,
                borderWidth: 0,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    grid: { color: colors.grid },
                    ticks: {
                        color: colors.text,
                        font: { family: "'Inter', sans-serif", size: 11 },
                        callback: v => v + ' kWh'
                    },
                    beginAtZero: true
                },
                y: {
                    grid: { display: false },
                    ticks: {
                        color: colors.text,
                        font: { family: "'Inter', sans-serif", size: 12, weight: '500' }
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: colors.tooltipBg,
                    titleColor: colors.tooltipText,
                    bodyColor: colors.tooltipText,
                    cornerRadius: 8,
                    padding: 12,
                    titleFont: { family: "'Inter', sans-serif", weight: '600' },
                    bodyFont: { family: "'Inter', sans-serif" },
                    callbacks: {
                        label: ctx => ` ${ctx.parsed.x} kWh/day`
                    }
                }
            }
        }
    });
}

/**
 * Create monthly cost comparison chart
 */
function createCostChart(canvasId, simulationData) {
    destroyChart(canvasId);
    const colors = getChartColors();
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = Object.keys(simulationData).map(k =>
        k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    );
    const data = Object.values(simulationData).map(v => v.monthly_cost);

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Monthly Cost (₹)',
                data: data,
                backgroundColor: colors.palette.slice(0, labels.length).map(c => c + 'cc'),
                borderWidth: 0,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        color: colors.text,
                        font: { family: "'Inter', sans-serif", size: 11 }
                    }
                },
                y: {
                    grid: { color: colors.grid },
                    ticks: {
                        color: colors.text,
                        font: { family: "'Inter', sans-serif", size: 11 },
                        callback: v => '₹' + v
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: colors.tooltipBg,
                    titleColor: colors.tooltipText,
                    bodyColor: colors.tooltipText,
                    cornerRadius: 8,
                    padding: 12,
                    callbacks: {
                        label: ctx => ` ₹${ctx.parsed.y.toFixed(2)}/month`
                    }
                }
            }
        }
    });
}

/**
 * Update all chart colors when theme changes
 */
function updateChartsTheme() {
    Object.keys(chartInstances).forEach(id => {
        const chart = chartInstances[id];
        if (!chart) return;
        const colors = getChartColors();

        // Update scales
        if (chart.options.scales) {
            Object.values(chart.options.scales).forEach(scale => {
                if (scale.ticks) scale.ticks.color = colors.text;
                if (scale.grid) scale.grid.color = colors.grid;
            });
        }

        // Update legend
        if (chart.options.plugins?.legend?.labels) {
            chart.options.plugins.legend.labels.color = colors.text;
        }

        chart.update('none');
    });
}
