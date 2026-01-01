# MOLO Parameter Sensitivity Study

Simple hydrostatic / eigenperiod study tool for MOLO-type floaters.

## Features

- Supports arbitrary number of columns (outer + center)
- Computes displacement, GM, hydrostatic stiffness
- Estimates heave and pitch/roll eigenperiods
- Includes heave added mass scaling from lower flanges / plates, calibrated against the MOLO Y7 15 MW reference

## Project Structure

- `floater_study.py` - Main analysis script
- `floater_study_notebook.ipynb` - Jupyter notebook for interactive analysis
- `FLOATER_STUDY_GUIDE.md` - Detailed usage guide

## Setup

1. **Python Environment**
   - Create a `.env` file in the project root with your Python path:
     ```
     PYTHON_PATH=C:\path\to\your\python.exe
     ```
   - Or if Python is in your PATH:
     ```
     PYTHON_PATH=python
     ```

2. **Install Dependencies**
   ```bash
   pip install numpy matplotlib jupyter
   ```

3. **Run the Analysis**
   ```bash
   python floater_study.py
   ```
   
   Or use the Jupyter notebook:
   ```bash
   jupyter notebook floater_study_notebook.ipynb
   ```

## Usage

See `FLOATER_STUDY_GUIDE.md` for detailed usage instructions and examples.

## Configuration

- `.env` - Contains the `PYTHON_PATH` variable for Cursor/VS Code
- `.vscode/settings.json` - Editor settings for Python interpreter
- `setup_python.ps1` - Helper script to load .env variables manually

