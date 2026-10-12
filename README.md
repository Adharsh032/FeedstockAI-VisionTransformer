# FEEDSTOCK.AI - Industry 4.0 Vision Transformer Defect Detection System

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Validation Accuracy](https://img.shields.io/badge/Validation%20Accuracy-94.8%25-brightgreen)](https://github.com/)
[![Status](https://img.shields.io/badge/Status-Patent%20Pending-blue)](https://github.com/)

> An Intelligent Vision Transformer (ViT)-based deep learning solution for automated feedstock visual quality inspection, multi-class surface defect segmentation, and Industry 4.0 real-time manufacturing decisions.

---

## Executive Summary and Academic Credits

- **Project Title:** Implementation of an Intelligent Vision Transformer-Based Deep Learning Model for Feedstock Quality Assessment and Defect Detection in Industry 4.0 Production Systems
- **Institution:** Department of Artificial Intelligence and Machine Learning, Manakula Vinayagar Institute of Technology, Pondicherry University, India
- **Investigators:**
  - **B. Adharsh Kumar** (Reg No: 23TN0016)
  - **Prasana B** (Reg No: 23TN0063)
  - **Jai Akash S** (Reg No: 23TN0036)
  - **Shaik Roshith A** (Reg No: 23TN0001)
- **Project Guide:** **Mr. S. Balaji**, Assistant Professor (AI & ML)
- **Patent Status:** Application in Progress (*Ref: FeedStock-ViT-2026*)

---

## System Architecture and Pipeline

`
+-----------------------------------------------------------------------------+
|                     FEEDSTOCK.AI PIPELINE ARCHITECTURE                      |
+-----------------------------------------------------------------------------+
  [Raw Feedstock Sheet]  (256 x 1600 px high-res industrial camera capture)
           |
           v
  [Patch Embedding]      (16 x 16 patches projected to 384-dimensional tokens)
           |
           v
  [Transformer Encoder]  (6-layer Multi-Head Self-Attention capturing long-range
           |              spatial dependencies across steel sheet surface)
           +-------------------------------+
           |                               |
           v                               v
  [Attention Rollout Engine]     [Multi-Task Classification Heads]
  (Recursive attention from        - Binary Defect Presence: P(Defect)
   [CLS] token to 2D heatmap)      - 4-Class Defect Categorization
           |                       - Automated Quality Grade: A / B / C
           v                               |
  [Defect Localization & Mask]             |
  (Fused ViT attention + surface           |
   texture gradient contours)              |
           |                               |
           +---------------+---------------+
                           |
                           v
  [Industry 4.0 Telemetry & Action Directive]
  - Bounding Boxes & Area % metrics
  - Quality Verdict (APPROVED / CONDITIONAL REWORK / QUARANTINE REJECT)
  - Printable Inspection Certificate & Real-Time Conveyor Stream
`

---

## Severstal Benchmark Defect Taxonomy

| Defect Class | Classification Name | Root Cause in Manufacturing | Recommended Industrial Action |
| :--- | :--- | :--- | :--- |
| **Grade A** | **Prime Defect-Free Material** | Optimal continuous casting and rolling | Approved for immediate forming and stamping |
| **Class 1** | **Pitted Surface / Inclusion** | Non-metallic slag entrapment or pinholes | Secondary structural forming; inspect casting nozzle |
| **Class 2** | **Surface Scratch / Crack** | Roll guide friction / mechanical abrasion | Polish guide stand #2; verify alignment |
| **Class 3** | **Scale / Crevice / Flaking** | Thermal cooling discrepancies and oxidation | Acid wash pickling line; boost descaling water jets |
| **Class 4** | **Severe Gouge / Deformation** | Heavy plastic indentation or tearing | Immediate shear quarantine to protect blanking dies |

---

## Key Features and Capabilities

1. **Real-Time Surface Inspection:**
   - Interactive zoom (50% to 400%) and smooth panning across high-resolution 256 x 1600 steel sheets.
   - 4-layer switchable overlay: **Bounding Boxes**, **ViT Attention Heatmap**, **Segmentation Mask**, and **Raw Image**.
   - Adjustable overlay opacity slider.
   - Dynamic scanning laser beam animation during inspection.
2. **20 Pre-Loaded Benchmark Samples:**
   - 1-click testing of ground-truth steel sheets (Prime material and Classes 1 through 4) with pre-verified RLE masks.
3. **Built-in 5,506 Dataset Test Images Browser:**
   - Integrated modal to search, browse, paginate, or randomly select from all 5,506 Severstal test images with 1-click instant AI diagnosis.
4. **Live Factory Conveyor Simulation:**
   - Real-time simulated industrial line scan camera streaming at 25 FPS with scanning HUD.
   - 1-click **Capture and Run Deep ViT Analysis** to freeze any live frame for diagnosis.
5. **Automated Batch Processing:**
   - Drag-and-drop multiple images simultaneously.
   - Aggregate statistics: pass rate, defect count, average quality score, and searchable per-sheet inspection table.
6. **Telemetry and Analytics Dashboard:**
   - Live Chart.js visualizations for Severstal benchmark class distribution and validation detections (94.8% accuracy, 0.932 F1-score).
   - Session history log with instant access to generated certificates.
7. **Official Industry 4.0 Inspection Certificates:**
   - 1-click generation of printable, professional Quality Inspection Certificates (HTML/PDF-ready).
   - Instant CSV log export for enterprise MES (Manufacturing Execution Systems).

---

## Project Organization

`
AI - Error detect/
|-- backend/                             # High-performance FastAPI Backend Service
|   |-- app.py                           # API routes, middleware, and static mounting
|   |-- config.py                        # Paths and server configuration
|   |-- schemas.py                       # Pydantic request and response models
|   |-- services/                        # Business and AI inference services
|   |   |-- inference_service.py         # End-to-end detector & history tracking
|   |   |-- camera_stream.py             # Factory conveyor camera simulator
|   |   |-- analytics_service.py         # Aggregated dataset and model statistics
|   |   -- report_service.py            # Certificate and CSV export generator
|   -- tests/
|       -- test_api.py                  # Automated test suite (7/7 passing)
|-- models/                              # Core AI and Vision Transformer Models
|   |-- vit_model.py                     # Multi-Head Attention ViT & Attention Rollout
|   |-- vit_feedstock_defect_model.pth   # 42.5 MB Trained PyTorch Model Weights
|   |-- model_metadata.json              # Architecture parameters & layer definitions
|   |-- defect_classifier.py             # End-to-end defect detection & quality grading
|   |-- defect_localizer.py              # Heatmaps, contours, masks, and bounding boxes
|   -- rle_codec.py                     # Run-Length Encoding (RLE) encoder/decoder
|-- frontend/                            # Modern Industry 4.0 Dark Glassmorphism UI
|   |-- index.html                       # Polished single-page web dashboard
|   |-- assets/                          # Favicon and icons
|   |-- css/
|   |   -- styles.css                   # Futuristic industrial styling & themes
|   -- js/
|       |-- app.js                       # Master application orchestrator
|       |-- viewer.js                    # Zoom/Pan interactive viewport engine
|       |-- analytics.js                 # Telemetry & Chart.js graph renderers
|       -- stream.js                    # Live conveyor camera stream controller
|-- data/                                # Dataset and Curated Benchmark Data
|   |-- samples/                         # 20 curated benchmark steel sheet images
|   |-- samples_metadata.json            # Ground-truth labels, classes, and RLE masks
|   -- severstal-steel-defect-detection/ # Severstal benchmark CSVs and test images
|-- docs/                                # Academic & Research Documentation
|   |-- patent/                          # Feed Stock Patent documentation (DOCX & PDF)
|   |-- reports/                         # Project evaluation reports and bonafide certs
|   |-- posters_and_presentations/       # Presentation slides and project posters
|   |-- journal/                         # Academic publication drafts
|   |-- research_papers/                 # 10 reference peer-reviewed literature papers
|   -- media/                           # Video demonstration and reference images
|-- notebooks/                           # Research & Prototyping Notebooks
|   |-- Feedstock_ViT_Local_Pipeline.ipynb # Local self-contained executable notebook
|   -- Feedstock_ViT_Project.ipynb      # Original Google Colab training notebook
|-- .vscode/                             # Visual Studio Code Run & Debug Configs
|   |-- launch.json                      # F5 debugging configurations
|   |-- tasks.json                       # Default build tasks (Ctrl+Shift+B)
|   |-- settings.json                    # Workspace settings & test discovery
|   -- extensions.json                  # Recommended VS Code extensions
|-- main.py                              # Root Python entrypoint for VS Code
|-- run_app.bat                          # Windows 1-click batch launcher
|-- run_app.ps1                          # Windows PowerShell launcher
|-- requirements.txt                     # Python dependencies
|-- .gitignore                           # Clean Git tracking configuration
-- README.md                            # Complete Project Documentation
`

---

## Quick Start Guide

### Option 1: Visual Studio Code (Recommended)
1. Open this project folder in **VS Code**:
   `ash
   code .
   `
2. **Press F5** or open main.py and click the **Run Python File** button in the top right corner.
3. The server starts and automatically opens your web browser to **http://localhost:8000**!

> **VS Code Features Included:**
> - **Pre-configured Debugger (.vscode/launch.json):** Press F5 to debug with breakpoints or hot-reload.
> - **Build Task (Ctrl+Shift+B):** Immediately starts the application via .vscode/tasks.json.
> - **Test Explorer:** Built-in test discovery for unit & integration tests.
> - **Jupyter Notebooks:** Open 
otebooks/Feedstock_ViT_Local_Pipeline.ipynb to step through model inference cell-by-cell.

### Option 2: One-Click Launcher (Windows)
Double-click 
un_app.bat (or execute 
un_app.ps1 in PowerShell).  
The server will start at http://localhost:8000/ and automatically launch your default browser!

### Option 3: Terminal Command Line
1. **Install Dependencies:**
   `ash
   pip install -r requirements.txt
   `
2. **Launch the Application:**
   `ash
   python main.py
   `
3. **Open the Web Dashboard:**
   - Dashboard: **http://localhost:8000**
   - Interactive API Docs (Swagger): **http://localhost:8000/docs**

---

## Running Automated Tests

Run the built-in unit and integration test suite:
`ash
python -m unittest backend/tests/test_api.py
`
*All 7 tests pass with sub-second execution.*

---

## REST API Reference

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| /api/health | GET | Health check and active AI engine status |
| /api/model/info | GET | Retrieve ViT architecture, parameter count, and weights status |
| /api/samples | GET | Retrieve 20 pre-loaded benchmark samples metadata |
| /api/samples/image/{filename} | GET | Serve raw benchmark feedstock image |
| /api/test-images | GET | List, search, and paginate 5,506 Severstal test images |
| /api/test-images/image/{filename} | GET | Serve raw test image file |
| /api/inspect/sample/{filename} | POST | Execute AI inspection on a benchmark sample |
| /api/inspect/test-image/{filename} | POST | Execute AI inspection on any of the 5,506 test images |
| /api/inspect/upload | POST | Upload custom steel sheet image for deep ViT inspection |
| /api/inspect/batch | POST | Inspect multiple images concurrently |
| /api/stream/video | GET | Live MJPEG industrial conveyor camera video feed |
| /api/analytics | GET | Retrieve model performance metrics & class distribution |
| /api/history | GET | Retrieve session inspection logs |
| /api/report/html/{id} | GET | Generate printable Industry 4.0 Inspection Certificate |
| /api/report/csv | GET | Download complete session inspection CSV audit log |

---

## References and Literature Citations

1. Dosovitskiy, A., et al. *An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale.* ICLR, 2021.
2. Severstal: *Steel Defect Detection - High-frequency surface inspection benchmark.* Kaggle Competition Dataset.
3. Singh, P. & Patel, A. *AI-Powered Feedstock Image Analysis for Manufacturing Quality Control.* IJAMT, 2023.
4. Wang, R., Jiang, T., & Li, S. *A Hybrid CNN-ViT Architecture for Metal Surface Defect Detection.* IEEE Access, 2023.
