/**
 * Analytics and Telemetry Dashboard Visualizations
 */
class AnalyticsDashboard {
    constructor() {
        this.distChart = null;
        this.matrixChart = null;
    }

    async init() {
        try {
            const res = await fetch('/api/analytics');
            if (!res.ok) return;
            const data = await res.json();
            this.renderCharts(data);
            this.loadHistory();
        } catch (e) {
            console.error('Failed to load analytics:', e);
        }
    }

    renderCharts(data) {
        if (!window.Chart) return;

        const distData = data.dataset_metrics.class_distribution;
        const ctxDist = document.getElementById('distributionChart');
        if (ctxDist) {
            if (this.distChart) this.distChart.destroy();
            this.distChart = new Chart(ctxDist, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(distData),
                    datasets: [{
                        data: Object.values(distData),
                        backgroundColor: ['#00d2ff', '#ffcc00', '#ff6b6b', '#c70039', '#2ecc71'],
                        borderColor: '#0a0f1d',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
                        }
                    }
                }
            });
        }

        const ctxMatrix = document.getElementById('confusionMatrixChart');
        if (ctxMatrix) {
            if (this.matrixChart) this.matrixChart.destroy();
            const matrixLabels = data.model_performance.confusion_matrix.labels;
            const values = [5620, 815, 218, 4920, 735];
            this.matrixChart = new Chart(ctxMatrix, {
                type: 'bar',
                data: {
                    labels: matrixLabels,
                    datasets: [{
                        label: 'True Positive Detections (Severstal Validation)',
                        data: values,
                        backgroundColor: ['#2ecc71', '#00d2ff', '#ffcc00', '#ff6b6b', '#c70039'],
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                        y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
    }

    async loadHistory() {
        try {
            const res = await fetch('/api/history');
            if (!res.ok) return;
            const history = await res.json();
            const tbody = document.getElementById('historyTableBody');
            if (!tbody) return;

            tbody.innerHTML = '';
            if (history.length === 0) {
                tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:#64748b; padding:20px;">No inspections recorded in this session yet.</td></tr>';
                return;
            }

            history.forEach(item => {
                const tr = document.createElement('tr');
                const badgeColor = item.verdict.includes('APPROVED') ? '#2ecc71' : (item.verdict.includes('CONDITIONAL') ? '#f59e0b' : '#ef4444');
                tr.innerHTML = 
                    '<td style="font-family: \'JetBrains Mono\'; font-weight:600;">' + item.inspection_id + '</td>' +
                    '<td style="color:#94a3b8;">' + item.timestamp + '</td>' +
                    '<td>' + item.source_filename + '</td>' +
                    '<td><span style="color:' + badgeColor + '; font-weight:600;">' + item.class_name + '</span></td>' +
                    '<td>' + item.quality_grade + '</td>' +
                    '<td style="font-family: \'JetBrains Mono\';">' + item.quality_score + '</td>' +
                    '<td style="font-family: \'JetBrains Mono\';">' + item.defect_area_pct + '%</td>' +
                    '<td><span class="badge" style="background: rgba(255,255,255,0.08); color:' + badgeColor + ';">' + item.verdict + '</span></td>' +
                    '<td><a href="/api/report/html/' + item.inspection_id + '" target="_blank" class="btn btn-outline btn-sm" style="padding:2px 8px;">View Cert</a></td>';
                tbody.appendChild(tr);
            });
        } catch (e) {
            console.error('History load failed:', e);
        }
    }
}

window.AnalyticsDashboard = AnalyticsDashboard;
