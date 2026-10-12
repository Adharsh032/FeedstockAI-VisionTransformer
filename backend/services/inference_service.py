import json
import uuid
import time
import datetime
import cv2
import numpy as np
from typing import List, Dict, Any, Optional

from backend.config import SAMPLES_META_PATH, SAMPLES_DIR
from models.defect_classifier import FeedstockDefectDetector


class InferenceService:
    def __init__(self):
        self.detector = FeedstockDefectDetector()
        self.samples_meta: List[Dict[str, Any]] = self._load_samples_meta()
        self.history: List[Dict[str, Any]] = []

    def _load_samples_meta(self) -> List[Dict[str, Any]]:
        if SAMPLES_META_PATH.exists():
            with open(SAMPLES_META_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def get_samples(self) -> List[Dict[str, Any]]:
        return self.samples_meta

    def inspect_sample(self, filename: str) -> Dict[str, Any]:
        match = next((s for s in self.samples_meta if s["filename"] == filename), None)
        img_path = SAMPLES_DIR / filename
        if not img_path.exists():
            raise FileNotFoundError(f"Sample file not found: {filename}")

        gt_rle = match.get("encoded_pixels") if match else None
        gt_class = match.get("class_id") if match else None

        result = self.detector.analyze_image(
            str(img_path),
            ground_truth_rle=gt_rle,
            ground_truth_class=gt_class
        )

        insp_id = f"INSP-{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "inspection_id": insp_id,
            "timestamp": ts,
            "source_filename": filename,
            **result
        }
        self._record_history(record)
        return record

    def inspect_image_bytes(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        nparr = np.frombuffer(file_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise ValueError("Invalid image file format")

        result = self.detector.analyze_image(img_bgr)

        insp_id = f"INSP-{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "inspection_id": insp_id,
            "timestamp": ts,
            "source_filename": filename,
            **result
        }
        self._record_history(record)
        return record

    def inspect_batch(self, items: List[tuple]) -> Dict[str, Any]:
        results = []
        batch_id = f"BATCH-{int(time.time())}-{uuid.uuid4().hex[:4].upper()}"
        start_time = time.time()

        for fname, fbytes in items:
            try:
                res = self.inspect_image_bytes(fbytes, fname)
                results.append(res)
            except Exception as e:
                results.append({
                    "inspection_id": f"ERR-{uuid.uuid4().hex[:6]}",
                    "source_filename": fname,
                    "error": str(e)
                })

        total = len(results)
        valid = [r for r in results if "error" not in r]
        defective = sum(1 for r in valid if r.get("is_defective"))
        defect_free = total - defective
        avg_score = round(sum(r.get("quality_score", 0) for r in valid) / max(len(valid), 1), 1)

        return {
            "batch_id": batch_id,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_inspected": total,
            "defective_count": defective,
            "defect_free_count": defect_free,
            "defect_rate_pct": round((defective / max(total, 1)) * 100, 2),
            "average_quality_score": avg_score,
            "processing_time_sec": round(time.time() - start_time, 2),
            "results": results
        }

    def _record_history(self, record: Dict[str, Any]):
        summary = {
            "inspection_id": record["inspection_id"],
            "timestamp": record["timestamp"],
            "source_filename": record["source_filename"],
            "is_defective": record["is_defective"],
            "class_id": record["class_id"],
            "class_name": record["class_name"],
            "verdict": record["verdict"],
            "quality_grade": record["quality_grade"],
            "quality_score": record["quality_score"],
            "defect_area_pct": record["defect_area_pct"],
            "regions_count": record["regions_count"]
        }
        self.history.insert(0, summary)
        if len(self.history) > 200:
            self.history.pop()

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history

    def get_inspection_by_id(self, insp_id: str) -> Optional[Dict[str, Any]]:
        for item in self.history:
            if item["inspection_id"] == insp_id:
                return item
        return None


# Global singleton instance
_inference_service: Optional[InferenceService] = None

def get_inference_service() -> InferenceService:
    global _inference_service
    if _inference_service is None:
        _inference_service = InferenceService()
    return _inference_service
