# Installation Instructions for mymt5

## Quick Setup

1. **Activate your virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Install the package in editable mode:**
   ```powershell
   pip install -e .
   ```

3. **Run the examples:**
   ```powershell
   python examples/08_validation.py
   ```

## Why this is needed

The `mymt5` package needs to be installed so Python can find it when you run the example scripts. Installing it in "editable" mode (the `-e` flag) means any changes you make to the source code will be reflected immediately without reinstalling.

## Alternative: Running without installation

If you don't want to install the package, you can add the project root to your Python path before running:

```powershell
$env:PYTHONPATH = "D:\GoogleDrive\Applications\mymt5"
python examples/08_validation.py
```

However, installing with `pip install -e .` is the recommended approach.

