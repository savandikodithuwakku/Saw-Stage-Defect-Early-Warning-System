# Saw Stage Defect Early Warning System

Analysis tools and datasets for detecting quality issues in a saw manufacturing process. The project combines sawing process data with quality-control measurements to explore anomaly and rework patterns and derive specification bounds.

## What This Project Does

This project helps a manufacturing team identify sawed parts that may fail during a later milling operation. A part can pass the existing saw-weight inspection and still develop a downstream quality problem. The project uses data recorded during the saw operation to provide an earlier warning.

In simple terms, the system:

1. Reads sensor measurements collected while each part is being sawed.
2. Extracts useful information from those measurements, such as power, feed, position, and vibration behavior.
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
- `Oct_Octabits_Presentation.pdf` and `Oct_Octabits_Report.pdf` - project presentation and report.

## Getting Started

1. Create and activate a Python environment.

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install the Python dependencies.

   ```powershell
   python -m pip install -r requirements.txt
   python -m pip install matplotlib seaborn jupyter ipykernel
   ```

3. Start Jupyter or open `Oct_Octabits_Notebook.ipynb` in VS Code.

   ```powershell
   jupyter notebook
   ```

4. Select the virtual environment as the notebook kernel and run the cells from top to bottom.

## Running the Dashboard

The dashboard consists of a FastAPI backend and a Vite frontend. Start each service in a separate PowerShell terminal from the project root.

### Backend

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8001
```

The API is available at <http://127.0.0.1:8001> and its interactive documentation at <http://127.0.0.1:8001/docs>.

### Frontend

```powershell
Set-Location frontend
npm install
npm run dev
```

Open <http://localhost:5173/> after both services are running. The frontend expects the backend at `http://127.0.0.1:8001/api`.

## Generating Metadata

`create_meta_jsons.py` calculates healthy-process bounds and reads specification limits. Before running it, update `DATASET_PATH` and `BASE_DIR` at the top of the file to point to the local dataset and metadata directories.

## Data Notes

The repository contains research and manufacturing-quality datasets used for analysis. Check the source and usage permissions before redistributing the data or derived results.