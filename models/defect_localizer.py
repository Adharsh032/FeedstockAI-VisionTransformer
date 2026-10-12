"""
Defect Localization & Computer Vision Visualization Engine
Generates heatmaps, bounding boxes, segmentation masks, and blended visual overlays.
"""

import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from typing import Tuple, List, Dict, Any, Optional

from models.rle_codec import extract_defect_regions, compute_mask_metrics


CLASS_COLORS = {
    0: (46, 204, 113),    # Green (Prime / Defect-Free)
    1: (0, 210, 255),     # Cyan / Sky Blue (Class 1: Pitted Surface)
    2: (255, 204, 0),     # Amber / Yellow (Class 2: Scratch / Crack)
    3: (255, 107, 107),    # Coral Red (Class 3: Scale / Crevice)
    4: (199, 0, 57),      # Crimson (Class 4: Gouge / Deformation)
}

CLASS_HEX = {
    0: "#2ecc71",
    1: "#00d2ff",
    2: "#ffcc00",
    3: "#ff6b6b",
    4: "#c70039"
}


def cv2_to_base64(img_bgr: np.ndarray, format: str = "JPEG", quality: int = 85) -> str:
    """Encodes OpenCV BGR image to base64 Data URL."""
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB) if len(img_bgr.shape) == 3 else img_bgr
    pil_img = Image.fromarray(rgb)
    buffered = BytesIO()
    pil_img.save(buffered, format=format, quality=quality)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    mime = "image/jpeg" if format.upper() == "JPEG" else "image/png"
    return f"data:{mime};base64,{img_str}"


def localize_defects_from_attention_and_texture(
    image_bgr: np.ndarray,
    vit_attention: np.ndarray,
    defect_probability: float,
    threshold: float = 0.38
) -> np.ndarray:
    """
    Combines Vision Transformer global attention with localized surface gradient anomalies.
    Returns a binary mask (256, 1600) with 1 where defects are located.
    """
    h, w = image_bgr.shape[:2]
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    if defect_probability < 0.45:
        # Defect-free prediction
        return np.zeros((h, w), dtype=np.uint8)

    # 1. Surface gradient & morphological defect analysis
    # Steel defects feature high local gradient or deep texture anomalies
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Multi-scale gradient
    grad_x = cv2.Sobel(enhanced, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(enhanced, cv2.CV_32F, 0, 1, ksize=3)
    grad_mag = cv2.magnitude(grad_x, grad_y)
    grad_norm = cv2.normalize(grad_mag, None, 0, 1.0, cv2.NORM_MINMAX)

    # 2. Resized ViT attention map
    attn_resized = cv2.resize(vit_attention, (w, h), interpolation=cv2.INTER_CUBIC)
    attn_norm = cv2.normalize(attn_resized, None, 0, 1.0, cv2.NORM_MINMAX)

    # 3. Fuse ViT attention with gradient anomalies
    # Anomaly score is strong where ViT attends and local variance is significant
    fused_score = 0.55 * attn_norm + 0.45 * grad_norm

    # Dynamic thresholding based on defect confidence
    sens_thresh = max(0.25, threshold - (defect_probability - 0.5) * 0.2)
    binary_mask = (fused_score > sens_thresh).astype(np.uint8)

    # Morphological cleanup (closing small gaps, removing isolated 1-pixel noise)
    kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel_close)
    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel_open)

    return binary_mask


def generate_heatmap_overlay(image_bgr: np.ndarray, heatmap: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """Blends ViT Attention Heatmap (Jet/Turbo colormap) on the steel image."""
    h, w = image_bgr.shape[:2]
    heat_resized = cv2.resize(heatmap, (w, h), interpolation=cv2.INTER_CUBIC)
    heat_u8 = np.uint8(255 * np.clip(heat_resized, 0, 1))

    # Apply Jet / Turbo colormap
    color_map = cv2.applyColorMap(heat_u8, cv2.COLORMAP_TURBO)
    blended = cv2.addWeighted(color_map, alpha, image_bgr, 1.0 - alpha, 0)
    return blended


def generate_mask_overlay(image_bgr: np.ndarray, mask: np.ndarray, class_id: int = 1, alpha: float = 0.45) -> np.ndarray:
    """Overlays colored defect segmentation mask on top of the image."""
    h, w = image_bgr.shape[:2]
    mask_resized = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)

    color_bgr = CLASS_COLORS.get(class_id, (0, 0, 255))[::-1]  # RGB to BGR
    overlay = image_bgr.copy()

    indices = mask_resized > 0
    if np.any(indices):
        blended_vals = (image_bgr[indices].astype(np.float32) * (1.0 - alpha) + np.array(color_bgr, dtype=np.float32) * alpha)
        overlay[indices] = blended_vals.astype(np.uint8)

    # Draw sharp contour borders around mask
    contours, _ = cv2.findContours(mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, color_bgr, 2)
    return overlay


def generate_bbox_overlay(
    image_bgr: np.ndarray,
    regions: List[Dict[str, Any]],
    class_name: str,
    class_id: int = 1
) -> np.ndarray:
    """Draws Industry 4.0 bounding boxes and telemetry tags on defect regions."""
    annotated = image_bgr.copy()
    color_bgr = CLASS_COLORS.get(class_id, (0, 0, 255))[::-1]

    for reg in regions:
        bbox = reg["bbox"]
        x, y, w, h = bbox["x"], bbox["y"], bbox["width"], bbox["height"]

        # Draw bounding box
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color_bgr, 2)

        # Draw tech tag
        tag = f"DEFECT #{reg['region_id']} ({reg['area_pixels']} px)"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.42
        thickness = 1
        (t_w, t_h), _ = cv2.getTextSize(tag, font, font_scale, thickness)

        # Background tag pill
        tag_y = max(y - 4, t_h + 4)
        cv2.rectangle(annotated, (x, tag_y - t_h - 4), (x + t_w + 6, tag_y + 2), (20, 24, 30), -1)
        cv2.rectangle(annotated, (x, tag_y - t_h - 4), (x + t_w + 6, tag_y + 2), color_bgr, 1)
        cv2.putText(annotated, tag, (x + 3, tag_y - 2), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    return annotated


def generate_all_visualizations(
    image_bgr: np.ndarray,
    mask: np.ndarray,
    heatmap: np.ndarray,
    regions: List[Dict[str, Any]],
    class_id: int,
    class_name: str
) -> Dict[str, str]:
    """Generates all visualization variants as Base64 images for direct UI rendering."""
    raw_b64 = cv2_to_base64(image_bgr)
    heatmap_img = generate_heatmap_overlay(image_bgr, heatmap, alpha=0.5)
    heatmap_b64 = cv2_to_base64(heatmap_img)

    mask_img = generate_mask_overlay(image_bgr, mask, class_id=class_id, alpha=0.45)
    mask_b64 = cv2_to_base64(mask_img)

    bbox_img = generate_bbox_overlay(mask_img, regions, class_name=class_name, class_id=class_id)
    bbox_b64 = cv2_to_base64(bbox_img)

    return {
        "raw_image": raw_b64,
        "heatmap_overlay": heatmap_b64,
        "mask_overlay": mask_b64,
        "bbox_overlay": bbox_b64
    }
