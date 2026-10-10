@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m src.npm_graph.main %*
) else (
    python -m src.npm_graph.main %*
)
exit /b %errorlevel%
