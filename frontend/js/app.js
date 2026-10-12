/**
 * Main Application Orchestrator
 */
class FeedstockApp {
    constructor() {
        this.viewer = new DefectImageViewer();
        this.analytics = new AnalyticsDashboard();
        this.stream = new StreamController();

        this.samples = [];
        this.currentInspection = null;
        this.soundEnabled = true;

        this.init();
    }

    async init() {
        if (window.lucide) {
            lucide.createIcons();
        }

        this.initNavTabs();
        this.initUploadEvents();
        this.initBatchEvents();
        this.initSound();

        await this.loadSamples();
        await this.analytics.init();

        // Auto-select first sample for initial preview
        if (this.samples.length > 0) {
            this.inspectSample(this.samples[0].filename);
        }
    }

    initNavTabs() {
        const tabs = document.querySelectorAll('.nav-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

                tab.classList.add('active');
                const targetId = tab.dataset.tab;
                const targetPane = document.getElementById(targetId);
                if (targetPane) targetPane.classList.add('active');

                if (targetId === 'tab-analytics') {
                    this.analytics.init();
                }

                if (window.lucide) lucide.createIcons();
            });
        });
    }

    initSound() {
        const btn = document.getElementById('soundToggleBtn');
        const icon = document.getElementById('soundIcon');
        if (btn) {
            btn.addEventListener('click', () => {
                this.soundEnabled = !this.soundEnabled;
                btn.style.opacity = this.soundEnabled ? '1.0' : '0.4';
                if (window.lucide) lucide.createIcons();
            });
        }
    }

    playSound(type) {
        if (!this.soundEnabled) return;
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);

            if (type === 'pass') {
                osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
                osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15); // A5
                gain.gain.setValueAtTime(0.08, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
                osc.start();
                osc.stop(ctx.currentTime + 0.3);
            } else {
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(320, ctx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(180, ctx.currentTime + 0.25);
                gain.gain.setValueAtTime(0.12, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
                osc.start();
                osc.stop(ctx.currentTime + 0.35);
            }
        } catch (e) {
            // Audio context not allowed until user gesture
        }
    }

    async loadSamples() {
        try {
            const res = await fetch('/api/samples');
            if (!res.ok) return;
            this.samples = await res.json();
            this.renderSampleCards(this.samples);
            this.initSampleFilters();
        } catch (e) {
            console.error('Error loading samples:', e);
        }
    }

    renderSampleCards(list) {
        const container = document.getElementById('samplesContainer');
        if (!container) return;
        container.innerHTML = '';

        // Permanent "+ Upload Custom Sheet" card as the first item
        const uploadCard = document.createElement('div');
        uploadCard.className = 'sample-card upload-trigger-card';
        uploadCard.title = 'Click to upload your own steel feedstock image for AI inspection';
        uploadCard.innerHTML = `
            <div class="sample-thumb-wrap upload-thumb">
                <i data-lucide="upload-cloud" class="upload-icon-pulse"></i>
            </div>
            <div class="sample-info">
                <span class="sample-badge" style="background: rgba(0, 210, 255, 0.25); color: #00d2ff;">+ CUSTOM</span>
                <div class="sample-name" style="font-weight:700; color:#00d2ff;">Upload Image</div>
                <div class="sample-meta">Browse local sheet</div>
            </div>
        `;
        uploadCard.addEventListener('click', () => {
            const globalInput = document.getElementById('globalFileInput');
            if (globalInput) globalInput.click();
        });
        container.appendChild(uploadCard);

        const badgeStyles = {
            0: { bg: 'rgba(46, 204, 113, 0.2)', color: '#2ecc71', label: 'Prime (A)' },
            1: { bg: 'rgba(0, 210, 255, 0.2)', color: '#00d2ff', label: 'C1: Pitted' },
            2: { bg: 'rgba(255, 204, 0, 0.2)', color: '#ffcc00', label: 'C2: Scratch' },
            3: { bg: 'rgba(255, 107, 107, 0.2)', color: '#ff6b6b', label: 'C3: Scale' },
            4: { bg: 'rgba(199, 0, 57, 0.2)', color: '#c70039', label: 'C4: Gouge' },
        };

        list.forEach(s => {
            const card = document.createElement('div');
            card.className = 'sample-card';
            card.dataset.filename = s.filename;
            const b = badgeStyles[s.class_id] || badgeStyles[0];

            card.innerHTML = `
                <div class="sample-thumb-wrap">
                    <img src="/api/samples/image/${s.filename}" class="sample-thumb" alt="${s.filename}" loading="lazy">
                </div>
                <div class="sample-info">
                    <span class="sample-badge" style="background:${b.bg}; color:${b.color};">${b.label}</span>
                    <div class="sample-name" title="${s.filename}">${s.filename}</div>
                    <div class="sample-meta">${s.is_defective ? `${s.defect_area_pct}% defect` : 'Pristine'}</div>
                </div>
            `;

            card.addEventListener('click', () => {
                document.querySelectorAll('.sample-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                this.inspectSample(s.filename);
            });

            container.appendChild(card);
        });
    }

    initSampleFilters() {
        const btns = document.querySelectorAll('.filter-btn');
        btns.forEach(btn => {
            btn.addEventListener('click', () => {
                btns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const f = btn.dataset.filter;

                if (f === 'all') {
                    this.renderSampleCards(this.samples);
                } else if (f === 'prime') {
                    this.renderSampleCards(this.samples.filter(s => s.class_id === 0));
                } else if (f === 'class1') {
                    this.renderSampleCards(this.samples.filter(s => s.class_id === 1));
                } else if (f === 'class2') {
                    this.renderSampleCards(this.samples.filter(s => s.class_id === 2));
                } else if (f === 'class3') {
                    this.renderSampleCards(this.samples.filter(s => s.class_id === 3));
                } else if (f === 'class4') {
                    this.renderSampleCards(this.samples.filter(s => s.class_id === 4));
                }
            });
        });
    }

    initUploadEvents() {
        const globalInput = document.getElementById('globalFileInput');
        const selectBtn = document.getElementById('selectFileBtn');
        const fileInput = document.getElementById('fileInput');
        const dropzone = document.getElementById('dropzonePlaceholder');
        const headerBtn = document.getElementById('uploadImageHeaderBtn');
        const viewerBtn = document.getElementById('uploadImageViewerBtn');
        const viewport = document.getElementById('viewportContainer');

        const triggerFileDialog = (e) => {
            if (e) e.stopPropagation();
            if (globalInput) {
                globalInput.value = '';
                globalInput.click();
            } else if (fileInput) {
                fileInput.value = '';
                fileInput.click();
            }
        };

        if (headerBtn) headerBtn.addEventListener('click', triggerFileDialog);
        if (viewerBtn) viewerBtn.addEventListener('click', triggerFileDialog);
        if (selectBtn) selectBtn.addEventListener('click', triggerFileDialog);
        if (dropzone) dropzone.addEventListener('click', triggerFileDialog);

        const handleFileSelection = (e) => {
            if (e.target.files && e.target.files.length > 0) {
                const fd = new FormData();
                fd.append('file', e.target.files[0]);
                this.inspectUpload(fd);
            }
        };

        if (globalInput) globalInput.addEventListener('change', handleFileSelection);
        if (fileInput) fileInput.addEventListener('change', handleFileSelection);

        // Allow Drag and drop onto the entire viewport canvas at all times
        if (viewport) {
            viewport.addEventListener('dragover', (e) => {
                e.preventDefault();
                viewport.classList.add('dragover');
            });
            viewport.addEventListener('dragleave', () => viewport.classList.remove('dragover'));
            viewport.addEventListener('drop', (e) => {
                e.preventDefault();
                viewport.classList.remove('dragover');
                if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                    const fd = new FormData();
                    fd.append('file', e.dataTransfer.files[0]);
                    this.inspectUpload(fd);
                }
            });
        }

        // Certificate button
        const certBtn = document.getElementById('downloadCertBtn');
        if (certBtn) {
            certBtn.addEventListener('click', () => {
                if (this.currentInspection) {
                    window.open(`/api/report/html/${this.currentInspection.inspection_id}`, '_blank');
                }
            });
        }
    }

    async inspectSample(filename) {
        this.viewer.startScanningAnimation();
        try {
            const res = await fetch(`/api/inspect/sample/${filename}`, { method: 'POST' });
            if (!res.ok) throw new Error('Inspection request failed');
            const data = await res.json();
            this.displayResults(data);
        } catch (e) {
            alert('Inspection failed: ' + e.message);
        } finally {
            this.viewer.stopScanningAnimation();
        }
    }

    async inspectUpload(formData) {
        this.viewer.startScanningAnimation();
        try {
            const res = await fetch('/api/inspect/upload', {
                method: 'POST',
                body: formData
            });
            if (!res.ok) throw new Error('Inspection upload failed');
            const data = await res.json();
            this.displayResults(data);
        } catch (e) {
            alert('Upload failed: ' + e.message);
        } finally {
            this.viewer.stopScanningAnimation();
        }
    }

    displayResults(data) {
        this.currentInspection = data;

        // Visualizations
        this.viewer.loadVisualizations(data.visualizations);

        // Timestamp
        document.getElementById('inspectionTimestamp').textContent = data.timestamp;

        // Verdict banner
        const banner = document.getElementById('verdictBanner');
        const vText = document.getElementById('verdictText');
        const vSub = document.getElementById('verdictSub');
        const vBadge = document.getElementById('gradeBadge');
        const vIcon = document.getElementById('verdictIcon');

        banner.className = 'verdict-banner-box';
        if (data.verdict.includes('APPROVED')) {
            banner.classList.add('approved');
            vIcon.setAttribute('data-lucide', 'check-circle-2');
            this.playSound('pass');
        } else if (data.verdict.includes('CONDITIONAL')) {
            banner.classList.add('conditional');
            vIcon.setAttribute('data-lucide', 'alert-triangle');
            this.playSound('alert');
        } else {
            banner.classList.add('quarantine');
            vIcon.setAttribute('data-lucide', 'x-octagon');
            this.playSound('alert');
        }

        vText.textContent = data.verdict;
        vSub.textContent = `Feedstock Quality: ${data.quality_grade} ? ${data.class_name}`;
        vBadge.textContent = data.quality_grade.split(' ')[0] + ' ' + data.quality_grade.split(' ')[1];

        // Metrics
        document.getElementById('metricScore').textContent = data.quality_score;
        document.getElementById('scoreBar').style.width = `${data.quality_score}%`;
        document.getElementById('metricArea').textContent = data.defect_area_pct;
        document.getElementById('metricPixels').textContent = `${data.total_defect_pixels.toLocaleString()} defect px`;
        document.getElementById('metricSeverity').textContent = data.severity;
        document.getElementById('metricConfidence').textContent = `Prob: ${(data.defect_probability * 100).toFixed(1)}%`;
        document.getElementById('metricRegions').textContent = data.regions_count;
        document.getElementById('metricMaxCluster').textContent = `Max: ${data.max_defect_region_area} px`;

        // Classification details
        const classBadge = document.getElementById('classBadge');
        classBadge.textContent = data.class_name;
        classBadge.style.color = data.class_color;
        document.getElementById('classDescription').textContent = data.class_metadata.description;

        // Probabilities breakdown
        const probsContainer = document.getElementById('probsContainer');
        probsContainer.innerHTML = '';
        Object.entries(data.class_probabilities).forEach(([k, v]) => {
            const row = document.createElement('div');
            row.className = 'prob-row';
            const pct = (v * 100).toFixed(1);
            row.innerHTML = `
                <span class="prob-name">${k}</span>
                <div class="prob-bar-wrap"><div class="prob-bar" style="width: ${pct}%;"></div></div>
                <span class="prob-pct">${pct}%</span>
            `;
            probsContainer.appendChild(row);
        });

        // Directive action
        document.getElementById('directiveAction').textContent = data.class_metadata.recommended_action;

        // Enable certificate download
        const certBtn = document.getElementById('downloadCertBtn');
        certBtn.disabled = false;

        if (window.lucide) lucide.createIcons();
    }

    initBatchEvents() {
        const batchSelectBtn = document.getElementById('batchSelectBtn');
        const batchFileInput = document.getElementById('batchFileInput');
        const batchDropzone = document.getElementById('batchDropzone');
        const batchSampleBtn = document.getElementById('batchSampleRunBtn');

        if (batchSelectBtn && batchFileInput) {
            batchSelectBtn.addEventListener('click', () => batchFileInput.click());
            batchDropzone.addEventListener('click', () => batchFileInput.click());

            batchFileInput.addEventListener('change', async (e) => {
                if (e.target.files.length > 0) {
                    await this.runBatchFiles(Array.from(e.target.files));
                }
            });
        }

        if (batchSampleBtn) {
            batchSampleBtn.addEventListener('click', async () => {
                batchSampleBtn.disabled = true;
                batchSampleBtn.innerHTML = '<i data-lucide="loader" class="spin"></i> Inspecting Samples...';
                if (window.lucide) lucide.createIcons();

                const results = [];
                for (const s of this.samples) {
                    try {
                        const r = await fetch(`/api/inspect/sample/${s.filename}`, { method: 'POST' });
                        if (r.ok) results.push(await r.json());
                    } catch (e) {}
                }

                const defective = results.filter(r => r.is_defective).length;
                const total = results.length;
                const avgScore = (results.reduce((acc, r) => acc + r.quality_score, 0) / Math.max(total, 1)).toFixed(1);

                this.renderBatchSummary({
                    total_inspected: total,
                    defective_count: defective,
                    defect_free_count: total - defective,
                    average_quality_score: avgScore,
                    results: results
                });

                batchSampleBtn.disabled = false;
                batchSampleBtn.innerHTML = '<i data-lucide="play"></i> Run All 20 Benchmark Samples';
                if (window.lucide) lucide.createIcons();
            });
        }
    }

    async runBatchFiles(files) {
        const fd = new FormData();
        files.forEach(f => fd.append('files', f));

        try {
            const res = await fetch('/api/inspect/batch', { method: 'POST', body: fd });
            if (!res.ok) throw new Error('Batch processing failed');
            const data = await res.json();
            this.renderBatchSummary(data);
        } catch (e) {
            alert('Batch error: ' + e.message);
        }
    }

    renderBatchSummary(batchData) {
        document.getElementById('batchMetricsRow').style.display = 'grid';
        document.getElementById('batchTableContainer').style.display = 'block';

        document.getElementById('batchTotal').textContent = batchData.total_inspected;
        document.getElementById('batchPass').textContent = batchData.defect_free_count;
        document.getElementById('batchFail').textContent = batchData.defective_count;
        document.getElementById('batchAvgScore').textContent = `${batchData.average_quality_score}%`;

        const tbody = document.getElementById('batchTableBody');
        tbody.innerHTML = '';

        batchData.results.forEach(r => {
            const tr = document.createElement('tr');
            const isDef = r.is_defective;
            const badgeColor = isDef ? '#ef4444' : '#2ecc71';

            tr.innerHTML = `
                <td>${r.source_filename}</td>
                <td><span style="color:${badgeColor}; font-weight:700;">${isDef ? 'DEFECT DETECTED' : 'PRIME / CLEAN'}</span></td>
                <td>${r.class_name}</td>
                <td>${r.quality_grade}</td>
                <td style="font-family:'JetBrains Mono';">${r.quality_score}</td>
                <td style="font-family:'JetBrains Mono';">${r.defect_area_pct}%</td>
                <td><span class="badge" style="background:rgba(255,255,255,0.08); color:${badgeColor};">${r.verdict}</span></td>
                <td>
                    <button class="btn btn-outline btn-sm view-in-main-btn" data-filename="${r.source_filename}" style="padding:2px 8px;">
                        Inspect
                    </button>
                </td>
            `;

            tr.querySelector('.view-in-main-btn').addEventListener('click', () => {
                document.querySelector('[data-tab="tab-inspect"]').click();
                this.displayResults(r);
            });

            tbody.appendChild(tr);
        });
    }
}

window.addEventListener('DOMContentLoaded', () => {
    window.appInstance = new FeedstockApp();
});
