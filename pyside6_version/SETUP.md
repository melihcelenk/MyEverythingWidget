# PySide6 Version - Quick Setup Guide

## Windows PowerShell Setup

```powershell
# 1. Navigate to project directory
cd C:\Kodlar\Desktop\MyEverythingWidget\pyside6_version

# 2. Create virtual environment (if not already created)
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 4. Upgrade pip
python -m pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt
pip install -r tests/visual/requirements.txt

# 6. Run the application
python main.py
```

## Windows CMD Setup

```cmd
# 1. Navigate to project directory
cd C:\Kodlar\Desktop\MyEverythingWidget\pyside6_version

# 2. Create virtual environment (if not already created)
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate.bat

# 4. Upgrade pip
python -m pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt
pip install -r tests/visual/requirements.txt

# 6. Run the application
python main.py
```

## Linux/Mac Setup

```bash
# 1. Navigate to project directory
cd /path/to/MyEverythingWidget/pyside6_version

# 2. Create virtual environment (if not already created)
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Upgrade pip
python -m pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt
pip install -r tests/visual/requirements.txt

# 6. Run the application
python main.py
```

## Running Tests

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Run unit tests
pytest tests/ -v

# Run visual tests (requires app to be running)
cd tests\visual
python run_visual_test.py
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'pip'"
- **Solution**: Make sure virtual environment is activated
  - PowerShell: `.\venv\Scripts\Activate.ps1`
  - CMD: `venv\Scripts\activate.bat`
  - Linux/Mac: `source venv/bin/activate`

### "pip: command not found"
- **Solution**: Use `python -m pip` instead of just `pip`
  - Example: `python -m pip install -r requirements.txt`

### "Execution Policy" error in PowerShell
- **Solution**: Run PowerShell as Administrator and execute:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Virtual environment not found
- **Solution**: Create it first:
  ```powershell
  python -m venv venv
  ```

## Verification

After setup, verify installation:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Check Python version
python --version

# Check installed packages
pip list

# Should see:
# - PySide6
# - pytest
# - pytest-qt
# - opencv-python (in visual tests)
# - numpy (in visual tests)
# - Pillow (in visual tests)
# - pyautogui (in visual tests)
```

