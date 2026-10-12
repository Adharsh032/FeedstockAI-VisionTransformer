"""
Run-Length Encoding (RLE) Codec and Mask Analysis Tools
Compatible with the Severstal Steel Defect Detection benchmark format.
"""

import numpy as np
import cv2
from typing import List, Dict, Any, Tuple, Optional


def rle_to_mask(rle_string: str, shape: Tuple[int, int] = (256, 1600)) -> np.ndarray:
    """
    Decodes Severstal Kaggle format RLE into a 2D binary numpy mask.
    The Severstal format uses column-major order (Fortran convention).
    """
    if not rle_string or not isinstance(rle_string, str) or rle_string.strip() == "":
        return np.zeros(shape, dtype=np.uint8)

    s = rle_string.strip().split()
    if len(s) < 2:
        return np.zeros(shape, dtype=np.uint8)

    starts = np.asarray(s[0::2], dtype=int) - 1
    lengths = np.asarray(s[1::2], dtype=int)
    ends = starts + lengths

    total_pixels = shape[0] * shape[1]
    mask_flat = np.zeros(total_pixels, dtype=np.uint8)

    for lo, hi in zip(starts, ends):
        if lo < total_pixels:
            mask_flat[lo:min(hi, total_pixels)] = 1

    return mask_flat.reshape(shape, order='F')


def mask_to_rle(mask: np.ndarray) -> str:
    """
    Encodes a 2D binary numpy mask into Severstal Kaggle format RLE.
    Uses column-major order (Fortran convention).
    """
    pixels = mask.T.flatten()
    pixels = np.concatenate([[0], pixels, [0]])
    runs = np.where(pixels[1:] != pixels[:-1])[0] + 1
    runs[1::2] -= runs[::2]
    return ' '.join(str(x) for x in runs)


def extract_defect_regions(mask: np.ndarray, min_area: int = 15) -> List[Dict[str, Any]]:
    """
    Extracts connected defect components, bounding boxes, and contours from a binary mask.
    """
    if mask is None or np.sum(mask) == 0:
        return []

    # Ensure uint8 binary mask (0 or 255)
    binary = (mask > 0).astype(np.uint8) * 255
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []
    for idx, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        # Approximate contour polygon to reduce payload size
        epsilon = 0.01 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        polygon = [[int(pt[0][0]), int(pt[0][1])] for pt in approx]

        regions.append({
            "region_id": idx + 1,
            "bbox": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
            "area_pixels": int(area),
            "perimeter": round(float(cv2.arcLength(cnt, True)), 2),
            "polygon": polygon
        })

    # Sort largest defect regions first
    regions.sort(key=lambda r: r["area_pixels"], reverse=True)
    return regions


def compute_mask_metrics(mask: np.ndarray, shape: Tuple[int, int] = (256, 1600)) -> Dict[str, Any]:
    """
    Computes statistical and geometric defect metrics for quality inspection.
    """
    if mask is None:
        return {
            "has_defect": False,
            "defect_pixels": 0,
            "total_pixels": shape[0] * shape[1],
            "defect_area_pct": 0.0,
            "regions_count": 0,
            "max_region_area": 0
        }

    total_pixels = shape[0] * shape[1]
    defect_pixels = int(np.sum(mask > 0))
    defect_pct = round((defect_pixels / total_pixels) * 100.0, 4) if total_pixels > 0 else 0.0

    regions = extract_defect_regions(mask)
    max_region = max([r["area_pixels"] for r in regions], default=0)

    return {
        "has_defect": defect_pixels > 0,
        "defect_pixels": defect_pixels,
        "total_pixels": total_pixels,
        "defect_area_pct": defect_pct,
        "regions_count": len(regions),
        "max_region_area": max_region,
        "regions": regions
    }
