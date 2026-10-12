/**
 * Interactive Defect Inspection Image Viewer & Pan/Zoom Engine
 */
class DefectImageViewer {
    constructor() {
        this.container = document.getElementById('viewportContainer');
        this.wrapper = document.getElementById('canvasWrapper');
        this.img = document.getElementById('mainInspectionImage');
        this.dropzone = document.getElementById('dropzonePlaceholder');
        this.beam = document.getElementById('scanningBeam');
        this.zoomLabel = document.getElementById('zoomLevel');
        this.opacityRange = document.getElementById('opacityRange');
        this.opacityVal = document.getElementById('opacityVal');

        this.zoom = 1.0;
        this.panX = 0;
        this.panY = 0;
        this.isDragging = false;
        this.startX = 0;
        this.startY = 0;

        this.currentLayer = 'bbox'; // bbox, heatmap, mask, raw
        this.visualizations = null;

        this.initEvents();
    }

    initEvents() {
        // Zoom controls
        const zoomInBtn = document.getElementById('zoomInBtn');
        const zoomOutBtn = document.getElementById('zoomOutBtn');
        const zoomResetBtn = document.getElementById('zoomResetBtn');

        if (zoomInBtn) zoomInBtn.addEventListener('click', () => this.setZoom(this.zoom + 0.25));
        if (zoomOutBtn) zoomOutBtn.addEventListener('click', () => this.setZoom(this.zoom - 0.25));
        if (zoomResetBtn) zoomResetBtn.addEventListener('click', () => this.resetTransform());

        // Mouse Pan
        if (this.wrapper) {
            this.wrapper.addEventListener('mousedown', (e) => {
                if (!this.img || this.img.style.display === 'none') return;
                this.isDragging = true;
                this.startX = e.clientX - this.panX;
                this.startY = e.clientY - this.panY;
                this.wrapper.style.cursor = 'grabbing';
            });

            window.addEventListener('mousemove', (e) => {
                if (!this.isDragging) return;
                this.panX = e.clientX - this.startX;
                this.panY = e.clientY - this.startY;
                this.updateTransform();
            });

            window.addEventListener('mouseup', () => {
                this.isDragging = false;
                if (this.wrapper) this.wrapper.style.cursor = 'grab';
            });

            // Wheel Zoom
            this.wrapper.addEventListener('wheel', (e) => {
                if (!this.img || this.img.style.display === 'none') return;
                e.preventDefault();
                const delta = e.deltaY < 0 ? 0.15 : -0.15;
                this.setZoom(this.zoom + delta);
            });
        }

        // Layer buttons
        document.querySelectorAll('.layer-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.layer-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentLayer = btn.dataset.layer;
                this.renderCurrentLayer();
            });
        });

        // Opacity slider
        if (this.opacityRange) {
            this.opacityRange.addEventListener('input', (e) => {
                const val = e.target.value;
                if (this.opacityVal) this.opacityVal.textContent = val + '%';
                if (this.img && this.currentLayer !== 'raw') {
                    this.img.style.opacity = val / 100;
                }
            });
        }

        // Fullscreen
        const fullscreenBtn = document.getElementById('fullscreenBtn');
        if (fullscreenBtn && this.container) {
            fullscreenBtn.addEventListener('click', () => {
                if (!document.fullscreenElement) {
                    this.container.requestFullscreen().catch(err => alert(err.message));
                } else {
                    document.exitFullscreen();
                }
            });
        }
    }

    setZoom(val) {
        this.zoom = Math.max(0.5, Math.min(4.0, val));
        if (this.zoomLabel) this.zoomLabel.textContent = Math.round(this.zoom * 100) + '%';
        this.updateTransform();
    }

    resetTransform() {
        this.zoom = 1.0;
        this.panX = 0;
        this.panY = 0;
        if (this.zoomLabel) this.zoomLabel.textContent = '100%';
        this.updateTransform();
    }

    updateTransform() {
        if (this.img) {
            this.img.style.transform = 'translate(' + this.panX + 'px, ' + this.panY + 'px) scale(' + this.zoom + ')';
        }
    }

    startScanningAnimation() {
        if (this.beam) this.beam.style.display = 'block';
    }

    stopScanningAnimation() {
        if (this.beam) this.beam.style.display = 'none';
    }

    loadVisualizations(visMap) {
        this.visualizations = visMap;
        if (this.dropzone) this.dropzone.style.display = 'none';
        if (this.img) this.img.style.display = 'block';
        this.resetTransform();
        this.renderCurrentLayer();
    }

    renderCurrentLayer() {
        if (!this.visualizations || !this.img) return;

        let src = '';
        if (this.currentLayer === 'bbox') {
            src = this.visualizations.bbox_overlay || this.visualizations.raw_image;
        } else if (this.currentLayer === 'heatmap') {
            src = this.visualizations.heatmap_overlay || this.visualizations.raw_image;
        } else if (this.currentLayer === 'mask') {
            src = this.visualizations.mask_overlay || this.visualizations.raw_image;
        } else {
            src = this.visualizations.raw_image;
        }

        this.img.src = src;
        const opacityValue = this.opacityRange ? (this.opacityRange.value / 100) : 0.85;
        this.img.style.opacity = (this.currentLayer === 'raw') ? '1.0' : opacityValue;
    }
}

window.DefectImageViewer = DefectImageViewer;
