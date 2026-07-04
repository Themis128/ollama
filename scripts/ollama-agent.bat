@echo off
setlocal

set "REPO_ROOT=%~dp0.."
pushd "%REPO_ROOT%"

REM Activate virtual environment if present
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Try Windows Terminal first; otherwise use standard cmd window.
where wt >NUL 2>NUL
if %ERRORLEVEL% EQU 0 (
    wt -w 0 new-tab python scripts\ollama-agent-terminal.py
) else (
    start "Ollama Agent" cmd /c "cd /d \"%REPO_ROOT%\" && if exist .venv (call .venv\Scripts\activate.bat) && python scripts\ollama-agent-terminal.py"
)

popd
endlocal
