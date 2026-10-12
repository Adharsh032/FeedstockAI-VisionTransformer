/**
 * Factory Conveyor Stream Controller
 */
class StreamController {
    constructor() {
        this.video = document.getElementById('streamVideo');
        this.captureBtn = document.getElementById('captureStreamBtn');
        this.initEvents();
    }

    initEvents() {
        if (this.captureBtn) {
            this.captureBtn.addEventListener('click', () => this.captureAndInspect());
        }
    }

    async captureAndInspect() {
        if (!this.video) return;

        // Switch to inspect tab
        document.querySelector('[data-tab=\"tab-inspect\"]').click();

        // Create canvas to capture current video frame
        const canvas = document.createElement('canvas');
        canvas.width = this.video.naturalWidth || 900;
        canvas.height = this.video.naturalHeight || 320;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(this.video, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append('file', blob, live_capture_.jpg);

            if (window.appInstance) {
                window.appInstance.inspectUpload(formData);
            }
        }, 'image/jpeg');
    }
}

window.StreamController = StreamController;
