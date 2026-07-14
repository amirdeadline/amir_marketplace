@echo off
REM Windows launcher shim for litellm-claude
set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%litellm_claude.py" %*
