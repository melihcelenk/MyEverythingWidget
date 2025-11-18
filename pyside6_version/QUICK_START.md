# Quick Start Guide

## ⚠️ IMPORTANT: Always Activate Virtual Environment First!

PySide6 is installed in the virtual environment, so you **must** activate it before running the app.

## Method 1: Quick Launcher (Easiest) ✅

Just double-click or run:
```powershell
.\run.bat          # Windows CMD
.\run.ps1          # Windows PowerShell
```

This automatically:
1. Activates the virtual environment
2. Runs the application

## Method 2: Manual Activation

```powershell
# Step 1: Activate virtual environment
.\venv\Scripts\Activate.ps1

# You should see (venv) in your prompt:
# (venv) PS C:\Kodlar\Desktop\MyEverythingWidget\pyside6_version>

# Step 2: Run the app
python main.py
```

## Method 3: One-Line Command

```powershell
.\venv\Scripts\Activate.ps1; python main.py
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'PySide6'"
**Problem**: Virtual environment is not activated.

**Solution**: 
```powershell
.\venv\Scripts\Activate.ps1
python main.py
```

### "Execution Policy" error in PowerShell
**Problem**: PowerShell script execution is disabled.

**Solution**: Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "venv\Scripts\Activate.ps1 cannot be loaded"
**Problem**: Script execution policy.

**Solution**: Use CMD instead:
```cmd
venv\Scripts\activate.bat
python main.py
```

Or use the `.bat` launcher:
```cmd
run.bat
```

## Verify Virtual Environment is Active

You should see `(venv)` at the start of your command prompt:
```
(venv) PS C:\Kodlar\Desktop\MyEverythingWidget\pyside6_version>
```

If you don't see `(venv)`, the virtual environment is **not active**!

