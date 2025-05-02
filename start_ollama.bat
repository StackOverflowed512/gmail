@echo off
echo Checking Ollama installation...

REM Check if Ollama is installed
ollama --version > nul 2>&1
if errorlevel 1 (
    echo Ollama is not installed!
    echo Please download and install Ollama from https://ollama.ai/download
    echo After installation, restart your computer
    echo.
    echo Press any key to open the download page...
    pause > nul
    start https://ollama.ai/download
    exit /b 1
)

echo Starting Ollama server...
start /b ollama serve

echo Waiting for Ollama to initialize...
timeout /t 10 /nobreak

echo Verifying Ollama model...
ollama list | findstr "mistral:7b-instruct-q4_K_M" > nul
if errorlevel 1 (
    echo Pulling Mistral model...
    ollama pull mistral:7b-instruct-q4_K_M
) else (
    echo Mistral model already downloaded
)

echo Ollama setup complete!