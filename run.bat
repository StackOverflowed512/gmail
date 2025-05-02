@echo off
echo Starting services...

REM Start Ollama
call start_ollama.bat

echo Starting backend...
cd backend
call venv\Scripts\activate
start python main.py
cd ..

echo Starting frontend...
cd frontend
start npm run dev
cd ..

echo Waiting for services to start...
timeout /t 5 /nobreak

echo Opening application...
start http://localhost:8000

echo Application is running!
echo Backend: http://localhost:7000
echo Frontend: http://localhost:8000
echo.
echo DO NOT CLOSE THIS WINDOW
pause