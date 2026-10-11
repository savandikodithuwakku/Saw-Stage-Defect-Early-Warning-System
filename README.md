# Saw-Stage Defect Early Warning System

An industrial quality-intelligence dashboard that identifies sawed parts at risk of failing during a later milling operation. It combines saw-process sensor data, quality-control records, engineered features, and a trained Random Forest model to provide an earlier inspection recommendation.

**Project team and contributors:** [Manody Asmini](https://github.com/manodyasasmini), [J.V. Ransika](https://github.com/jv-ransika), [Dinith Rathnayaka](https://github.com/dinithrathnayaka23), and [Savandi Kodithuwakku](https://github.com/savandikodithuwakku).

## What This Project Does

During manufacturing, a part can pass the existing saw-weight inspection and still fail during a later milling operation. This project analyses signals recorded while a part is being sawed, such as power, feed, position, and vibration, to identify patterns linked to downstream quality problems and provide an earlier warning.

1. Reads sensor measurements collected while each part is being sawed.
2. Extracts useful information from those measurements, including power, feed, position, and vibration behaviour.
3. Uses a trained Random Forest model to calculate a risk score for each part.
4. Recommends either `Continue` for a low-risk part or `Inspection recommended` for a part that should be checked before milling.
5. Lets an operator investigate an individual part and view its sensor signals, model result, and historical quality outcome.

The dashboard is a demonstration and decision-support tool. It does not replace quality inspections or guarantee that every defect will be detected. Its purpose is to help operators focus attention on parts that show patterns associated with previous downstream failures.

## Project Structure

- `app/` contains the FastAPI backend and the logic for loading model results and product investigations.
- `frontend/` contains the React and Vite dashboard used to view the results.
- `artifacts/` contains the exported model, benchmark results, feature importance, and dashboard metadata.
- `scripts/` contains the training and export script used to create the model artifacts.
- The CSV, HDF5, and notebook files contain the source process and quality-control data used for analysis.

## Contents

- `Oct_Octabits_Notebook.ipynb` - main exploratory analysis notebook.
- `sawing_qc_data.csv` and `sawing_quality_data.csv` - sawing quality-control data.
- `pneumatic_cylinders_qc_data.csv` and `cylinder_bottoms_qc_data.csv` - downstream quality-control data.
- `anomalous_parts_detailed.csv` - detailed records for anomalous parts.
- `sampled_saw_process_data.h5` - sampled saw-process measurements in HDF5 format.
- `sawing_field_keys.csv` - field descriptions for the sawing data.
- `spezifikationsgrenze.csv` - specification limits used in the analysis.
- `create_meta_jsons.py` - utility for calculating bounds and creating metadata JSON files.

## Getting Started

The project includes both a FastAPI backend and a Vite frontend. Follow the [installation](#installation) and [run the application](#run-the-application) instructions below to start the complete dashboard locally.

## Project Links

| Resource | Link |
| --- | --- |
| Frontend dashboard | [`frontend/`](frontend/) |
| Backend/API source | [`app/`](app/) |
| Full GitHub repository | [Saw-Stage-Defect-Early-Warning-System](https://github.com/savandikodithuwakku/Saw-Stage-Defect-Early-Warning-System) |
| API documentation | `http://127.0.0.1:8001/docs` when running locally |

## Features

### Dashboard and operator workflow

| Feature | Description |
| --- | --- |
| Overview dashboard | Summarises documented saw misalignments, saw-weight QC results, and later milling failures. |
| Process workflow view | Shows the path from saw sensor data through active-cut extraction, feature engineering, Random Forest scoring, and the final decision. |
| Product investigation | Searches for a product ID and displays its model result, risk score, recommendation, and historical outcome. |
| Risk-based recommendation | Classifies parts as `Continue` or `Inspection recommended` using the configured risk threshold of `0.25`. |
| Sensor signal charts | Displays active-cut Power, Feed, Position, and Vibration signals for the selected product. |
| Historical QC context | Compares saw-weight QC, milling QC, and the known target outcome after the prediction. |
| Model performance view | Reports precision, recall, accuracy, false-positive rate, F1-score, and the confusion matrix for the benchmark. |
| Feature importance | Visualises the most influential engineered features used by the final Random Forest model. |
| Loading and error states | Explains when dashboard data is loading or when the API is unavailable. |

### Data and machine learning

| Feature | Description |
| --- | --- |
| Sensor-data analysis | Uses sampled saw-process measurements stored in HDF5 format. |
| Active-cut extraction | Isolates measurements recorded while the saw is actively cutting. |
| Feature engineering | Derives statistical process features from power, feed, position, and vibration signals. |
| Random Forest prediction | Produces a risk score for each benchmark product. |
| Benchmark evaluation | Stores exported metrics, model comparison results, feature importance, and benchmark predictions. |
| Early-warning analysis | Provides metadata for understanding how early a potentially problematic part can be identified. |
| Specification analysis | Supports healthy-process bounds and specification-limit metadata. |

### Backend API

| Endpoint | Purpose |
| --- | --- |
| `GET /api/overview` | Returns dashboard overview statistics. |
| `GET /api/pipeline` | Returns the process pipeline stages. |
| `GET /api/benchmark/metrics` | Returns benchmark model metrics and confusion-matrix values. |
| `GET /api/benchmark/products` | Returns benchmark products and their predictions. |
| `GET /api/model-comparison` | Returns model comparison metadata. |
| `GET /api/model-features` | Returns the leading model features. |
| `GET /api/early-warning` | Returns early-warning analysis data. |
| `GET /api/business-value` | Returns business-value metadata. |
| `GET /api/limitations` | Returns documented model limitations. |
| `GET /api/predict/{product_id}` | Returns the prediction for one product. |
| `GET /api/investigation/{product_id}` | Returns product details, QC context, and downsampled sensor signals. |

## Technology Stack

| Area | Technology | Role |
| --- | --- | --- |
| Frontend | React, TypeScript, Vite | Interactive dashboard and development server |
| Frontend charts | Recharts | Sensor signal and model visualisations |
| Frontend icons | Lucide React | Consistent interface icons |
| Backend | FastAPI, Uvicorn | REST API and local ASGI server |
| Data processing | Python, Pandas, NumPy, SciPy, h5py | Data loading, cleaning, and signal processing |
| Machine learning | scikit-learn | Random Forest training and evaluation |
| Model persistence | joblib | Exporting and loading the trained model |
| Analysis | Jupyter Notebook | Exploratory analysis and investigation |

## Repository Structure

| Path | Purpose |
| --- | --- |
| `app/` | FastAPI application, schemas, data access, and product investigation logic |
| `frontend/` | React/Vite dashboard source and frontend dependencies |
| `artifacts/` | Exported model, metrics, benchmark products, metadata, and analysis results |
| `scripts/train_and_export.py` | Trains the model and exports dashboard artifacts |
| `Oct_Octabits_Notebook.ipynb` | Main exploratory analysis notebook |
| `*.csv` | Process, quality-control, anomaly, field-key, and specification data |
| `sampled_saw_process_data.h5` | Sampled saw-process sensor measurements |
| `create_meta_jsons.py` | Generates process-bound and metadata JSON files |

## Installation

### Prerequisites

- Python 3.10 or newer
- Node.js and npm
- Git
- PowerShell on Windows, or an equivalent shell on macOS/Linux

### 1. Clone the repository

```powershell
git clone https://github.com/savandikodithuwakku/Saw-Stage-Defect-Early-Warning-System.git
Set-Location "Saw-Stage-Defect-Early-Warning-System"
```

### 2. Create the Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For notebook-based analysis, install the optional analysis tools:

```powershell
python -m pip install matplotlib seaborn jupyter ipykernel
```

### 3. Install frontend dependencies

```powershell
Set-Location frontend
npm install
Set-Location ..
```

## Run the Application

Start the backend and frontend in two separate terminals from the repository root.

### Terminal 1: Backend/API

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8001
```

Backend URLs:

- API: <http://127.0.0.1:8001>
- Interactive API docs: <http://127.0.0.1:8001/docs>

### Terminal 2: Frontend

```powershell
Set-Location frontend
npm run dev
```

Open <http://localhost:5173/> in a browser. The frontend is configured to request data from `http://127.0.0.1:8001/api`.

## Run the Notebook

```powershell
jupyter notebook
```

Open `Oct_Octabits_Notebook.ipynb`, select the `.venv` Python environment as the kernel, and run the notebook cells from top to bottom.

## Train and Export the Model

The training workflow is in [`scripts/train_and_export.py`](scripts/train_and_export.py). It creates or updates the files in `artifacts/`, which are consumed by the backend and dashboard. Confirm that the required source datasets are available before running it.

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/train_and_export.py
```

## Data and Limitations

The repository contains research and manufacturing-quality datasets. Confirm the source and usage permissions before redistributing the data or derived artifacts. The model is evaluated on a fixed benchmark and should be validated with representative production data before operational use. A high or low risk score is an aid to investigation, not proof that a part will pass or fail.

## License

This project is licensed under the [MIT License](LICENSE). The license permits use, modification, distribution, and private or commercial use, subject to the conditions in the license text.