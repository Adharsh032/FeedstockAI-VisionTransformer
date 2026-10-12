"""
Backend Application Configuration
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
SAMPLES_DIR = DATA_DIR / "samples"
SAMPLES_META_PATH = DATA_DIR / "samples_metadata.json"
DATASET_DIR = DATA_DIR / "severstal-steel-defect-detection"
FRONTEND_DIR = BASE_DIR / "frontend"
DOCS_DIR = BASE_DIR / "docs"

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

APP_TITLE = "Industry 4.0 Feedstock Defect Detection & Quality AI"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Vision Transformer (ViT) Surface Defect Detection & Quality Assessment System"

TEST_IMAGES_DIR = DATASET_DIR / "test_images"
