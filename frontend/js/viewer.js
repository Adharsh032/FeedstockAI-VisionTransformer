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
        document.getElementById('zoomInBtn').addEventListener('click', () => this.setZoom(this.zoom + 0.25));
        document.getElementById('zoomOutBtn').addEventListener('click', () => this.setZoom(this.zoom - 0.25));
        document.getElementById('zoomResetBtn').addEventListener('click', () => this.resetTransform());

        // Mouse Pan
        this.wrapper.addEventListener('mousedown', (e) => {
            if (this.img.style.display === 'none') return;
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
            this.wrapper.style.cursor = 'grab';
        });

        // Wheel Zoom
        this.wrapper.addEventListener('wheel', (e) => {
            if (this.img.style.display === 'none') return;
            e.preventDefault();
            const delta = e.deltaY < 0 ? 0.15 : -0.15;
            this.setZoom(this.zoom + delta);
        });

        // Layer buttons
        document.querySelectorAll('.layer-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.layer-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentLayer = btn.dataset.layer;
                this.renderCurrentLayer();
            });
        });

        // Opacity slider
        this.opacityRange.addEventListener('input', (e) => {
            const val = e.target.value;
            this.opacityVal.textContent = ${val}%;
            if (this.currentLayer !== 'raw') {
                this.img.style.opacity = val / 100;
            }
        });

        // Fullscreen
        document.getElementById('fullscreenBtn').addEventListener('click', () => {
            if (!document.fullscreenElement) {
                this.container.requestFullscreen().catch(err => alert(err.message));
            } else {
                document.exitFullscreen();
            }
        });
    }

    setZoom(val) {
        this.zoom = Math.max(0.5, Math.min(4.0, val));
        this.zoomLabel.textContent = ${Math.round(this.zoom * 100)}%;
        this.updateTransform();
    }

    resetTransform() {
        this.zoom = 1.0;
        this.panX = 0;
        this.panY = 0;
        this.zoomLabel.textContent = '100%';
        this.updateTransform();
    }

    updateTransform() {
        this.img.style.transform = 	ranslate(px, px) scale();
    }

    startScanningAnimation() {
        this.beam.style.display = 'block';
    }

    stopScanningAnimation() {
        this.beam.style.display = 'none';
    }

    loadVisualizations(visMap) {
        this.visualizations = visMap;
        this.dropzone.style.display = 'none';
        this.img.style.display = 'block';
        this.resetTransform();
        this.renderCurrentLayer();
    }

    renderCurrentLayer() {
        if (!this.visualizations) return;

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
        this.img.style.opacity = (this.currentLayer === 'raw') ? '1.0' : (this.opacityRange.value / 100);
    }
}

window.DefectImageViewer = DefectImageViewer;
