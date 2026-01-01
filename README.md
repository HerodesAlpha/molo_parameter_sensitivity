# Python Environment Configuration

This project is configured to use a Python interpreter specified in a `.env` file.

## Setup

1. Create a `.env` file in the project root with your Python path:
   ```
   PYTHON_PATH=C:\path\to\your\python.exe
   ```
   
   Or if Python is in your PATH:
   ```
   PYTHON_PATH=python
   ```

2. **Option A: Automatic (Recommended)**
   - The terminal profile is configured to automatically load `.env` variables
   - Open a new terminal in Cursor and it will load the variables
   - Cursor should pick up the Python interpreter automatically

3. **Option B: Manual Setup**
   - Run the `setup_python.ps1` script in PowerShell:
     ```powershell
     .\setup_python.ps1
     ```
   - Then restart Cursor or reload the window (Ctrl+Shift+P → "Reload Window")

## Configuration Files

- `.env` - Contains the `PYTHON_PATH` variable
- `.vscode/settings.json` - Cursor/VS Code settings that reference the Python path
- `setup_python.ps1` - Helper script to load .env variables manually

## Notes

- After updating `.env`, you may need to restart Cursor or reload the window
- The Python extension will use the interpreter specified in `PYTHON_PATH`
- If `${env:PYTHON_PATH}` doesn't work, you can set the path directly in `.vscode/settings.json`

