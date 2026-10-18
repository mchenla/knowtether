@echo off
setlocal DisableDelayedExpansion
rem Arguments remain data. Do not use CALL or construct shell code from paths.
for %%K in (python.exe python3.exe) do (
    %%K -B "%~dp0plugin_entry.py" "%~1" 2>nul
    if not errorlevel 1 exit /b 0
)
py.exe -3 -B "%~dp0plugin_entry.py" "%~1" 2>nul
if not errorlevel 1 exit /b 0
echo {"systemMessage":"[KnowTether PYTHON_REQUIRED] Python 3.10+ is required on PATH; hook skipped."}
exit /b 0
