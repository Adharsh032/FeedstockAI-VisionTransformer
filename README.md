# FEEDSTOCK.AI --- Steel Surface Defect Detection

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

FEEDSTOCK.AI is a research project exploring Vision Transformer
(ViT)-based inspection of steel surfaces. It is designed to classify
surface defects, visualize potential defect regions, and present
inspection results through a web dashboard for manufacturing
quality-control workflows.

> **Project note:** Performance figures and patent status should be
> published only when they have been verified and can be supported by
> project records.

## Contents

-   [Overview](#overview)
-   [Features](#features)
-   [System Pipeline](#system-pipeline)
-   [Technology Stack](#technology-stack)
-   [Dataset](#dataset)
-   [Project Structure](#project-structure)
-   [Getting Started](#getting-started)
-   [Running Tests](#running-tests)
-   [API Reference](#api-reference)
-   [Project Team](#project-team)
-   [References](#references)

## Overview

The project combines a Vision Transformer model with image-processing
and backend services to support steel-sheet inspection. The intended
workflow is to submit or select a steel-surface image, run model
inference, view predicted defects and visual explanations, and review or
export inspection records.

The implementation described in this repository includes a FastAPI
backend, a browser-based dashboard, model inference utilities, benchmark
samples, analytics, and report-generation services.

## Features

-   **Image inspection:** Submit a steel-surface image for model
    inference.
-   **Defect visualization:** View available heatmaps, masks, contours,
    and bounding-box overlays.
-   **Benchmark samples:** Run inspections on curated sample images.
-   **Test-image browser:** Search and inspect images from the Severstal
    test set when the dataset files are available locally.
-   **Batch inspection:** Process multiple images and review aggregate
    results.
-   **Conveyor simulation:** View a simulated industrial camera stream.
-   **Analytics and history:** Review session inspection records and
    model statistics.
-   **Report export:** Generate printable inspection reports and export
    session records as CSV.
-   **API documentation:** Explore available endpoints through FastAPI's
    Swagger UI.

Feature availability depends on the code, model weights, and dataset
files included in the local checkout.

## System Pipeline

``` text
Steel-surface image
        |
        v
Image preprocessing
        |
        v
Vision Transformer inference
        |
        +----------------------+
        |                      |
        v                      v
Defect classification     Attention / localization
        |                      |
        +-----------+----------+
                    |
                    v
        Inspection result and visualizations
                    |
                    v
       Dashboard, history, and report export
```

## Technology Stack

  Component                     Technology
  ----------------------------- --------------------------------------
  Language                      Python 3.11+
  Deep learning                 PyTorch
  Vision model                  Vision Transformer (ViT)
  API backend                   FastAPI
  Request/response validation   Pydantic
  Dashboard                     HTML, CSS, JavaScript
  Charts                        Chart.js
  Dataset benchmark             Severstal Steel Defect Detection
  Development tools             Visual Studio Code, Jupyter Notebook

## Dataset

The project references the **Severstal: Steel Defect Detection** dataset
hosted on Kaggle.

Dataset access and local file placement may be required for browsing the
full test set or running dataset-based evaluations. Review the dataset's
license and terms before redistribution. Do not commit large dataset
archives or private data to the repository.

## Project Structure

``` text
AI-Error-detect/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── schemas.py
│   ├── services/
│   │   ├── inference_service.py
│   │   ├── camera_stream.py
│   │   ├── analytics_service.py
│   │   └── report_service.py
│   └── tests/
│       └── test_api.py
├── models/
│   ├── vit_model.py
│   ├── defect_classifier.py
│   ├── defect_localizer.py
│   ├── rle_codec.py
│   └── model_metadata.json
├── frontend/
│   ├── index.html
│   ├── assets/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── app.js
│       ├── viewer.js
│       ├── analytics.js
│       └── stream.js
├── data/
│   ├── samples/
│   └── samples_metadata.json
├── docs/
├── notebooks/
├── .vscode/
├── main.py
├── run_app.bat
├── run_app.ps1
├── requirements.txt
├── .gitignore
└── README.md
```

The tree is a guide to the intended layout. Some folders and files,
including trained model weights and dataset assets, may be omitted from
a Git checkout because of their size or licensing.

## Getting Started

### Prerequisites

-   Python 3.11 or a compatible version supported by the dependencies
-   Git
-   The project source code
-   Model weights and dataset assets, if required by the selected
    feature

### 1. Clone the repository

Replace the placeholder URL with the URL of your GitHub repository.

``` bash
git clone <YOUR_REPOSITORY_URL>
cd AI-Error-detect
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt**

``` bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Start the application

From the project root, run:

``` bash
python main.py
```

If the repository's Windows launcher scripts are present, you can also
use `run_app.bat` or `run_app.ps1`.

Open the dashboard at:

-   **Dashboard:** http://localhost:8000
-   **Interactive API documentation:** http://localhost:8000/docs
-   **Alternative API documentation:** http://localhost:8000/redoc

If the application uses a different port in your local configuration,
use the URL printed in the terminal.

## Running Tests

Run the API test suite from the project root:

``` bash
python -m unittest backend/tests/test_api.py
```

The test result depends on the installed dependencies, configuration,
model files, and dataset assets available in your environment.

## API Reference

The following endpoints are described by the project implementation.
Confirm the current route definitions in `backend/app.py` before relying
on them.

  --------------------------------------------------------------------------------------
  Method                  Endpoint                               Purpose
  ----------------------- -------------------------------------- -----------------------
  `GET`                   `/api/health`                          Check service health

  `GET`                   `/api/model/info`                      Retrieve model
                                                                 information

  `GET`                   `/api/samples`                         List curated benchmark
                                                                 samples

  `GET`                   `/api/samples/image/{filename}`        Retrieve a sample image

  `GET`                   `/api/test-images`                     Search or paginate test
                                                                 images

  `GET`                   `/api/test-images/image/{filename}`    Retrieve a test image

  `POST`                  `/api/inspect/sample/{filename}`       Inspect a benchmark
                                                                 sample

  `POST`                  `/api/inspect/test-image/{filename}`   Inspect a test-set
                                                                 image

  `POST`                  `/api/inspect/upload`                  Inspect an uploaded
                                                                 image

  `POST`                  `/api/inspect/batch`                   Inspect multiple images

  `GET`                   `/api/stream/video`                    Access the simulated
                                                                 camera stream

  `GET`                   `/api/analytics`                       Retrieve analytics

  `GET`                   `/api/history`                         Retrieve session
                                                                 history

  `GET`                   `/api/report/html/{id}`                Generate an inspection
                                                                 report

  `GET`                   `/api/report/csv`                      Export inspection
                                                                 records
  --------------------------------------------------------------------------------------

## Project Team

**Institution:** Department of Artificial Intelligence and Machine
Learning, Manakula Vinayagar Institute of Technology, affiliated with
Pondicherry University, India.

**Project contributors** - B. Adharsh Kumar - Prasana B. - Jai Akash
S. - Shaik Roshith A.

**Project guide:** Mr. S. Balaji, Assistant Professor, AI & ML.

## References

1.  Dosovitskiy, A., et al. "An Image is Worth 16x16 Words: Transformers
    for Image Recognition at Scale." *International Conference on
    Learning Representations (ICLR)*, 2021.
2.  Kaggle. "Severstal: Steel Defect Detection."
    https://www.kaggle.com/c/severstal-steel-defect-detection
3.  Vaswani, A., et al. "Attention Is All You Need." *Advances in Neural
    Information Processing Systems*, 2017.

## License

No license has been specified in this README. Add a `LICENSE` file
before presenting the repository as open source, and ensure that dataset
and model assets can legally be redistributed.
