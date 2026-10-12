import os
import io
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import (
    FRONTEND_DIR, SAMPLES_DIR, APP_TITLE, APP_VERSION, APP_DESCRIPTION
)
from backend.services.inference_service import get_inference_service
from backend.services.camera_stream import get_camera_simulator
from backend.services.analytics_service import get_system_analytics
from backend.services.report_service import generate_csv_report, generate_html_certificate


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- API Endpoints ----------------- #

@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    fav = FRONTEND_DIR / "assets" / "favicon.ico"
    if fav.exists():
        return FileResponse(fav, media_type="image/x-icon")
    return Response(status_code=204)

@app.get("/api/model/info")
async def model_info():
    from pathlib import Path
    import json
    meta_path = Path("models/model_metadata.json")
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    else:
        meta = {
            "model_name": "Feedstock Vision Transformer (ViT-Patch16-224)",
            "total_parameters": 11142920,
            "patch_size": "16x16 pixels"
        }
    service = get_inference_service()
    meta["active_device"] = service.detector.device
    return meta

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "system": APP_TITLE,
        "version": APP_VERSION,
        "engine": "Vision Transformer (ViT-Patch16-224)",
        "docs": "/docs"
    }


@app.get("/api/samples")
async def list_samples():
    service = get_inference_service()
    return service.get_samples()


@app.get("/api/samples/image/{filename}")
async def get_sample_image(filename: str):
    path = SAMPLES_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Sample image not found")
    return FileResponse(path, media_type="image/jpeg")


@app.get("/api/test-images")
async def list_test_images(page: int = 1, limit: int = 24, query: str = ""):
    from backend.config import TEST_IMAGES_DIR
    if not TEST_IMAGES_DIR.exists():
        return {"images": [], "total": 0, "page": page, "total_pages": 0, "limit": limit}

    all_names = [f.name for f in TEST_IMAGES_DIR.glob("*.jpg")]
    if query and query.strip():
        q = query.strip().lower()
        filtered = [n for n in all_names if q in n.lower()]
    else:
        filtered = all_names

    total = len(filtered)
    total_pages = max(1, (total + limit - 1) // limit)
    page = max(1, min(page, total_pages))
    start = (page - 1) * limit
    end = start + limit
    page_items = filtered[start:end]

    return {
        "images": page_items,
        "total": total,
        "page": page,
        "total_pages": total_pages,
        "limit": limit
    }


@app.get("/api/test-images/image/{filename}")
async def get_test_image_file(filename: str):
    from backend.config import TEST_IMAGES_DIR
    path = TEST_IMAGES_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Test image not found")
    return FileResponse(path, media_type="image/jpeg")


@app.post("/api/inspect/test-image/{filename}")
async def inspect_test_image_endpoint(filename: str):
    service = get_inference_service()
    try:
        result = service.inspect_test_image(filename)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Test image not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/inspect/sample/{filename}")
async def inspect_sample_endpoint(filename: str):
    service = get_inference_service()
    try:
        result = service.inspect_sample(filename)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Sample image not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/inspect/upload")
async def inspect_upload_endpoint(file: UploadFile = File(...)):
    service = get_inference_service()
    try:
        content = await file.read()
        result = service.inspect_image_bytes(content, file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inspection failed: {str(e)}")


@app.post("/api/inspect/batch")
async def inspect_batch_endpoint(files: List[UploadFile] = File(...)):
    service = get_inference_service()
    items = []
    for f in files:
        b = await f.read()
        items.append((f.filename, b))

    try:
        batch_summary = service.inspect_batch(items)
        return batch_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stream/video")
async def stream_conveyor_video():
    sim = get_camera_simulator()
    return StreamingResponse(
        sim.generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/api/analytics")
async def analytics_endpoint():
    return get_system_analytics()


@app.get("/api/history")
async def history_endpoint():
    service = get_inference_service()
    return service.get_history()


@app.delete("/api/history")
async def clear_history_endpoint():
    service = get_inference_service()
    service.history.clear()
    return {"message": "Inspection history cleared"}


@app.get("/api/report/csv")
async def export_csv_endpoint():
    service = get_inference_service()
    csv_data = generate_csv_report(service.get_history())
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inspection_log.csv"}
    )


@app.get("/api/report/html/{inspection_id}")
async def get_html_report(inspection_id: str):
    service = get_inference_service()
    item = service.get_inspection_by_id(inspection_id)
    if not item:
        # Fallback to current history first item
        history = service.get_history()
        item = history[0] if history else {"inspection_id": inspection_id}

    html = generate_html_certificate(item)
    return HTMLResponse(content=html)


# ----------------- Static Frontend Mounting ----------------- #

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
async def serve_index():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse("<h1>Feedstock Defect Detection API Online</h1><p><a href='/docs'>Swagger Docs</a></p>")
