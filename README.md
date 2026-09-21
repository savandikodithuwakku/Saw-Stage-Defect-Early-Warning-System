# Saw Stage Defect Early Warning System

Analysis tools and datasets for detecting quality issues in a saw manufacturing process. The project combines sawing process data with quality-control measurements to explore anomaly and rework patterns and derive specification bounds.

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

2. Install the notebook dependencies.

   ```powershell
   python -m pip install numpy pandas matplotlib seaborn scikit-learn h5py jupyter ipykernel
   ```

3. Start Jupyter or open `Oct_Octabits_Notebook.ipynb` in VS Code.

   ```powershell
   jupyter notebook
   ```

4. Select the virtual environment as the notebook kernel and run the cells from top to bottom.

## Generating Metadata

`create_meta_jsons.py` calculates healthy-process bounds and reads specification limits. Before running it, update `DATASET_PATH` and `BASE_DIR` at the top of the file to point to the local dataset and metadata directories.

## Data Notes

The repository contains research and manufacturing-quality datasets used for analysis. Check the source and usage permissions before redistributing the data or derived results.