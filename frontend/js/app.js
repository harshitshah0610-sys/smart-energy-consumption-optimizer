/**
 * Smart Energy Consumption Optimizer — Main Application Logic
 * Handles form interactions, API calls, navigation, and UI state.
 */

// ============================================================
// State
// ============================================================
const AppState = {
    appliances: [],
    predictionResult: null,
    optimizationResult: null,
    simulationResult: null,
    availableAppliances: {},
    applianceCategories: {}
};

const API_BASE = ''; // Same-origin

// ============================================================
// Initialization
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initThemeToggle();
    loadApplianceList();
    addDefaultAppliances();
    
    // Bind form actions
    document.getElementById('btn-add-appliance').addEventListener('click', addApplianceRow);
    document.getElementById('btn-predict').addEventListener('click', runPrediction);
    document.getElementById('btn-optimize').addEventListener('click', runOptimization);
    document.getElementById('btn-simulate').addEventListener('click', runSimulation);
    document.getElementById('btn-export-pdf').addEventListener('click', exportPDF);
});

// ============================================================
// Navigation
// ============================================================
function initNavigation() {
    const navBtns = document.querySelectorAll('.header__nav-btn');
    
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-section');
            switchSection(target);
            
            // Update active state
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
}

function switchSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    const target = document.getElementById(sectionId);
    if (target) {
        target.classList.add('active');
    }
}

function navigateTo(sectionId) {
    switchSection(sectionId);
    document.querySelectorAll('.header__nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-section') === sectionId);
    });
}

// ============================================================
// Theme Toggle
// ============================================================
function initThemeToggle() {
    const toggle = document.getElementById('theme-toggle');
    const saved = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);
    
    toggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateThemeIcon(next);
        
        // Update charts for new theme
        if (typeof updateChartsTheme === 'function') {
            updateChartsTheme();
        }
    });
}

function updateThemeIcon(theme) {
    const toggle = document.getElementById('theme-toggle');
    toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    toggle.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
}

// ============================================================
// Appliance Management
// ============================================================
async function loadApplianceList() {
    try {
        const res = await fetch(`${API_BASE}/api/appliances`);
        const data = await res.json();
        if (data.success) {
            AppState.availableAppliances = data.appliances;
            AppState.applianceCategories = data.categories;
        }
    } catch (err) {
        console.warn('Could not load appliance list, using defaults');
    }
}

function addDefaultAppliances() {
    const defaults = [
        { name: 'ceiling_fan', quantity: 3, hours: 10 },
        { name: 'led_light', quantity: 5, hours: 6 },
        { name: 'refrigerator', quantity: 1, hours: 24 },
        { name: 'tv', quantity: 1, hours: 4 },
    ];
    
    defaults.forEach(app => {
        AppState.appliances.push({ ...app, id: Date.now() + Math.random() });
    });
    
    renderApplianceList();
}

function addApplianceRow() {
    AppState.appliances.push({
        id: Date.now() + Math.random(),
        name: 'fan',
        quantity: 1,
        hours: 4
    });
    renderApplianceList();
}

function removeAppliance(id) {
    AppState.appliances = AppState.appliances.filter(a => a.id !== id);
    renderApplianceList();
}

function updateAppliance(id, field, value) {
    const app = AppState.appliances.find(a => a.id === id);
    if (app) {
        app[field] = field === 'name' ? value : parseFloat(value) || 0;
    }
}

function renderApplianceList() {
    const container = document.getElementById('appliance-list');
    
    const applianceOptions = [
        'fan', 'ceiling_fan', 'ac', 'led_light', 'tube_light',
        'refrigerator', 'tv', 'washing_machine', 'microwave',
        'water_heater', 'geyser', 'computer', 'laptop', 'iron',
        'mixer_grinder', 'water_pump', 'router', 'phone_charger',
        'exhaust_fan', 'cooler', 'heater', 'induction_cooktop'
    ];
    
    container.innerHTML = AppState.appliances.map(app => `
        <div class="appliance-item" data-id="${app.id}">
            <select class="form-select" 
                    onchange="updateAppliance(${app.id}, 'name', this.value)"
                    aria-label="Select appliance">
                ${applianceOptions.map(opt => `
                    <option value="${opt}" ${app.name === opt ? 'selected' : ''}>
                        ${formatName(opt)}
                    </option>
                `).join('')}
            </select>
            <input type="number" class="form-input" value="${app.quantity}" min="1" max="20"
                   onchange="updateAppliance(${app.id}, 'quantity', this.value)"
                   placeholder="Qty" aria-label="Quantity">
            <input type="number" class="form-input" value="${app.hours}" min="0" max="24" step="0.5"
                   onchange="updateAppliance(${app.id}, 'hours', this.value)"
                   placeholder="Hours/day" aria-label="Hours per day">
            <button class="btn btn--danger btn-remove" onclick="removeAppliance(${app.id})" 
                    title="Remove appliance" aria-label="Remove appliance">✕</button>
        </div>
    `).join('');
}

function formatName(name) {
    return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// ============================================================
// Prediction
// ============================================================
async function runPrediction() {
    const rooms = parseInt(document.getElementById('input-rooms').value) || 2;
    const occupants = parseInt(document.getElementById('input-occupants').value) || 3;
    const temperature = parseFloat(document.getElementById('input-temperature').value) || 30;
    
    if (AppState.appliances.length === 0) {
        showToast('Please add at least one appliance', 'error');
        return;
    }
    
    const btn = document.getElementById('btn-predict');
    btn.classList.add('btn--loading');
    btn.disabled = true;
    
    try {
        const res = await fetch(`${API_BASE}/api/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                rooms,
                occupants,
                temperature,
                appliances: AppState.appliances.map(a => ({
                    name: a.name,
                    quantity: a.quantity,
                    hours: a.hours
                }))
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            AppState.predictionResult = data.prediction;
            renderPredictionResults(data.prediction);
            navigateTo('section-results');
            showToast('Prediction complete!', 'success');
        } else {
            showToast(data.error || 'Prediction failed', 'error');
        }
    } catch (err) {
        showToast('Connection error. Is the server running?', 'error');
        console.error(err);
    } finally {
        btn.classList.remove('btn--loading');
        btn.disabled = false;
    }
}

function renderPredictionResults(prediction) {
    // Update stat cards
    document.getElementById('stat-daily-kwh').textContent = prediction.daily_kwh;
    document.getElementById('stat-monthly-kwh').textContent = prediction.monthly_kwh;
    document.getElementById('stat-monthly-cost').textContent = '₹' + prediction.monthly_cost.toLocaleString();
    document.getElementById('stat-model-accuracy').textContent = 
        (prediction.model_accuracy * 100).toFixed(1) + '%';
    
    // Temperature impact badge
    const tempImpact = document.getElementById('stat-temp-impact');
    if (tempImpact) {
        const impact = prediction.temperature_impact;
        tempImpact.textContent = (impact >= 0 ? '+' : '') + impact + ' kWh';
        tempImpact.style.color = impact > 0 ? '#f59e0b' : '#10b981';
    }
    
    // Render breakdown chart
    if (prediction.appliance_breakdown && prediction.appliance_breakdown.length > 0) {
        createBreakdownChart('chart-breakdown', prediction.appliance_breakdown);
    }
    
    // Render trend chart
    createTrendChart('chart-trend', prediction.daily_kwh);
    
    // Show results section
    document.getElementById('results-content').classList.remove('hidden');
    document.getElementById('results-empty').classList.add('hidden');
}

// ============================================================
// Optimization
// ============================================================
async function runOptimization() {
    if (!AppState.predictionResult) {
        showToast('Please run prediction first', 'error');
        navigateTo('section-input');
        return;
    }
    
    const rooms = parseInt(document.getElementById('input-rooms').value) || 2;
    const occupants = parseInt(document.getElementById('input-occupants').value) || 3;
    const temperature = parseFloat(document.getElementById('input-temperature').value) || 30;
    
    const btn = document.getElementById('btn-optimize');
    btn.classList.add('btn--loading');
    btn.disabled = true;
    
    try {
        const res = await fetch(`${API_BASE}/api/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                rooms,
                occupants,
                temperature,
                appliances: AppState.predictionResult.appliance_breakdown
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            AppState.optimizationResult = data.optimization;
            renderOptimizationResults(data.optimization);
            navigateTo('section-optimization');
            showToast('Optimization complete!', 'success');
        } else {
            showToast(data.error || 'Optimization failed', 'error');
        }
    } catch (err) {
        showToast('Connection error', 'error');
        console.error(err);
    } finally {
        btn.classList.remove('btn--loading');
        btn.disabled = false;
    }
}

function renderOptimizationResults(opt) {
    // Savings comparison
    document.getElementById('opt-original-kwh').textContent = opt.original_daily_kwh + ' kWh';
    document.getElementById('opt-original-cost').textContent = '₹' + opt.original_monthly_cost.toLocaleString() + '/month';
    document.getElementById('opt-optimized-kwh').textContent = opt.optimized_daily_kwh + ' kWh';
    document.getElementById('opt-optimized-cost').textContent = '₹' + opt.optimized_monthly_cost.toLocaleString() + '/month';
    document.getElementById('opt-saving-percent').textContent = '-' + opt.percentage_reduction + '%';
    
    // Stats row
    document.getElementById('opt-stat-daily').textContent = opt.daily_saving_kwh + ' kWh';
    document.getElementById('opt-stat-monthly').textContent = '₹' + opt.monthly_cost_saving.toLocaleString();
    document.getElementById('opt-stat-yearly').textContent = '₹' + opt.yearly_cost_saving.toLocaleString();
    
    // Efficiency rating
    const rating = opt.efficiency_rating;
    const circle = document.getElementById('efficiency-circle');
    const grade = document.getElementById('efficiency-grade');
    const label = document.getElementById('efficiency-label');
    const score = document.getElementById('efficiency-score');
    
    circle.style.borderColor = rating.color;
    circle.style.setProperty('--glow-color', rating.color);
    grade.textContent = rating.grade;
    grade.style.color = rating.color;
    label.textContent = rating.label;
    score.textContent = 'Score: ' + rating.score + '/100';
    
    // Recommendations
    const recList = document.getElementById('recommendation-list');
    recList.innerHTML = opt.recommendations.map(rec => {
        const icons = {
            shift: '⏰',
            reduce: '📉',
            occupancy: '👥',
            weather: '🌡️'
        };
        return `
            <div class="recommendation-item" data-priority="${rec.priority}">
                <div class="recommendation-item__icon recommendation-item__icon--${rec.type}">
                    ${icons[rec.type] || '💡'}
                </div>
                <div class="recommendation-item__content">
                    <div class="recommendation-item__message">${rec.message}</div>
                    <div class="recommendation-item__saving">
                        Save ${rec.saving_kwh} kWh/day
                        ${rec.priority === 'high' ? ' • High Impact' : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    // General tips
    const tipsGrid = document.getElementById('tips-grid');
    tipsGrid.innerHTML = opt.general_tips.map(tip => `
        <div class="tip-card">
            <span class="tip-card__icon">${tip.icon}</span>
            <span>${tip.tip}</span>
        </div>
    `).join('');
    
    // Comparison chart
    createComparisonChart('chart-comparison', opt.optimized_appliances);
    
    // Schedule
    renderSchedule(opt.schedule);
    
    // Show content
    document.getElementById('optimization-content').classList.remove('hidden');
    document.getElementById('optimization-empty').classList.add('hidden');
}

function renderSchedule(schedule) {
    const grid = document.getElementById('schedule-grid');
    const slotNames = {
        early_morning: '🌅 Early Morning',
        morning: '☀️ Morning',
        afternoon: '🌤️ Afternoon',
        evening: '🌇 Evening',
        night: '🌙 Night',
        late_night: '🌑 Late Night'
    };
    
    grid.innerHTML = Object.entries(schedule).map(([key, slot]) => `
        <div class="schedule-slot">
            <div class="schedule-slot__name">${slotNames[key] || key}</div>
            <div class="schedule-slot__time">${slot.time}</div>
            <div class="schedule-slot__items">
                ${slot.appliances.length > 0 
                    ? slot.appliances.map(a => `
                        <div class="schedule-slot__item schedule-slot__item--${a.status}">
                            <span>${getApplianceEmoji(a.name)}</span>
                            <span>${a.name}</span>
                        </div>
                    `).join('')
                    : '<div class="text-muted text-sm">No appliances scheduled</div>'
                }
            </div>
        </div>
    `).join('');
}

function getApplianceEmoji(name) {
    const emojis = {
        fan: '🌀', ceiling_fan: '🌀', ac: '❄️', air_conditioner: '❄️',
        led_light: '💡', light: '💡', tube_light: '💡',
        refrigerator: '🧊', fridge: '🧊', tv: '📺', television: '📺',
        washing_machine: '👕', microwave: '📦', water_heater: '🔥',
        geyser: '🔥', computer: '💻', laptop: '💻', iron: '♨️',
        mixer_grinder: '🔧', water_pump: '💧', router: '📡',
        phone_charger: '🔋', exhaust_fan: '🌬️', cooler: '💨',
        heater: '🔥', induction_cooktop: '🍳'
    };
    return emojis[name.toLowerCase().replace(/ /g, '_')] || '🔌';
}

// ============================================================
// Simulation
// ============================================================
async function runSimulation() {
    if (AppState.appliances.length === 0) {
        showToast('Please add appliances first', 'error');
        navigateTo('section-input');
        return;
    }
    
    const rooms = parseInt(document.getElementById('input-rooms').value) || 2;
    const occupants = parseInt(document.getElementById('input-occupants').value) || 3;
    const temperature = parseFloat(document.getElementById('input-temperature').value) || 30;
    
    const btn = document.getElementById('btn-simulate');
    btn.classList.add('btn--loading');
    btn.disabled = true;
    
    try {
        const res = await fetch(`${API_BASE}/api/simulate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                rooms,
                occupants,
                temperature,
                appliances: AppState.appliances.map(a => ({
                    name: a.name,
                    quantity: a.quantity,
                    hours: a.hours
                }))
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            AppState.simulationResult = data.simulation;
            renderSimulationResults(data.simulation);
            showToast('Simulation complete!', 'success');
        } else {
            showToast(data.error || 'Simulation failed', 'error');
        }
    } catch (err) {
        showToast('Connection error', 'error');
        console.error(err);
    } finally {
        btn.classList.remove('btn--loading');
        btn.disabled = false;
    }
}

function renderSimulationResults(sim) {
    // Render scenario charts
    createScenarioChart('chart-scenario', sim);
    createCostChart('chart-cost', sim);
    
    // Statistics table
    const tbody = document.getElementById('simulation-table-body');
    tbody.innerHTML = Object.entries(sim).map(([key, val]) => {
        const currentKwh = sim.current.daily_kwh;
        const diff = val.daily_kwh - currentKwh;
        const diffPct = ((diff / currentKwh) * 100).toFixed(1);
        const diffClass = diff > 0 ? 'color: var(--accent-rose)' : 'color: var(--accent-emerald)';
        
        return `
            <tr>
                <td style="font-weight: 600; text-transform: capitalize">
                    ${key.replace(/_/g, ' ')}
                </td>
                <td>${val.daily_kwh} kWh</td>
                <td>${val.monthly_kwh} kWh</td>
                <td>₹${val.monthly_cost.toLocaleString()}</td>
                <td style="${diffClass}; font-weight: 600">
                    ${key === 'current' ? '—' : (diff >= 0 ? '+' : '') + diffPct + '%'}
                </td>
            </tr>
        `;
    }).join('');
    
    document.getElementById('simulation-content').classList.remove('hidden');
    document.getElementById('simulation-empty').classList.add('hidden');
}

// ============================================================
// PDF Export
// ============================================================
async function exportPDF() {
    showToast('Generating PDF report...', 'info');
    
    try {
        // Use browser print as PDF (simple, no extra library needed)
        const printWindow = window.open('', '_blank');
        
        const prediction = AppState.predictionResult;
        const optimization = AppState.optimizationResult;
        
        if (!prediction) {
            showToast('Please run prediction first', 'error');
            return;
        }
        
        let html = `
<!DOCTYPE html>
<html>
<head>
    <title>Energy Report — Smart Energy Optimizer</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; color: #1e293b; max-width: 800px; margin: auto; }
        h1 { color: #3b82f6; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }
        h2 { color: #475569; margin-top: 30px; }
        .stat { display: inline-block; padding: 15px 25px; margin: 8px; background: #f1f5f9; border-radius: 10px; text-align: center; }
        .stat-value { font-size: 24px; font-weight: 800; color: #3b82f6; }
        .stat-label { font-size: 12px; color: #64748b; text-transform: uppercase; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid #e2e8f0; }
        th { background: #f1f5f9; color: #475569; font-size: 12px; text-transform: uppercase; }
        .highlight { color: #10b981; font-weight: 600; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 12px; }
        .rec { padding: 10px; margin: 5px 0; background: #f0fdf4; border-left: 3px solid #10b981; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>⚡ Smart Energy Consumption Report</h1>
    <p>Generated: ${new Date().toLocaleDateString('en-IN', { dateStyle: 'full' })}</p>
    
    <h2>📊 Energy Prediction</h2>
    <div>
        <div class="stat"><div class="stat-value">${prediction.daily_kwh}</div><div class="stat-label">Daily kWh</div></div>
        <div class="stat"><div class="stat-value">${prediction.monthly_kwh}</div><div class="stat-label">Monthly kWh</div></div>
        <div class="stat"><div class="stat-value">₹${prediction.monthly_cost}</div><div class="stat-label">Monthly Cost</div></div>
    </div>
    
    <h2>🔌 Appliance Breakdown</h2>
    <table>
        <tr><th>Appliance</th><th>Qty</th><th>Hours/Day</th><th>Wattage</th><th>Daily kWh</th></tr>
        ${prediction.appliance_breakdown.map(a => `
            <tr>
                <td>${a.name}</td>
                <td>${a.quantity}</td>
                <td>${a.hours}h</td>
                <td>${a.wattage}W</td>
                <td><strong>${a.daily_kwh}</strong></td>
            </tr>
        `).join('')}
    </table>`;
        
        if (optimization) {
            html += `
    <h2>✅ Optimization Results</h2>
    <div>
        <div class="stat"><div class="stat-value highlight">-${optimization.percentage_reduction}%</div><div class="stat-label">Reduction</div></div>
        <div class="stat"><div class="stat-value highlight">₹${optimization.monthly_cost_saving}</div><div class="stat-label">Monthly Savings</div></div>
        <div class="stat"><div class="stat-value highlight">₹${optimization.yearly_cost_saving}</div><div class="stat-label">Yearly Savings</div></div>
        <div class="stat"><div class="stat-value">${optimization.efficiency_rating.grade}</div><div class="stat-label">Efficiency Rating</div></div>
    </div>
    
    <h2>💡 Recommendations</h2>
    ${optimization.recommendations.map(r => `
        <div class="rec">${r.message} <span class="highlight">(Save ${r.saving_kwh} kWh/day)</span></div>
    `).join('')}`;
        }
        
        html += `
    <div class="footer">
        <p>Report generated by Smart Energy Consumption Optimizer (HomeHostel)</p>
        <p>This is an AI-generated analysis based on the provided inputs.</p>
    </div>
</body>
</html>`;
        
        printWindow.document.write(html);
        printWindow.document.close();
        
        // Trigger print dialog after a short delay
        setTimeout(() => {
            printWindow.print();
        }, 500);
        
        showToast('PDF report ready — use the print dialog to save', 'success');
        
    } catch (err) {
        showToast('Could not generate PDF', 'error');
        console.error(err);
    }
}

// ============================================================
// Toast Notifications
// ============================================================
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.innerHTML = `<span>${icons[type] || ''}</span><span>${message}</span>`;
    
    container.appendChild(toast);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
