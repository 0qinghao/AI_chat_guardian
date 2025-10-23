@echo off

echo.

set KMP_DUPLICATE_LIB_OK=TRUE

python gui.py

if errorlevel 1 (
    echo.
    pause
)
