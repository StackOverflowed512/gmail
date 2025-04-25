@echo off
echo Starting backend...
cd backend
call venv\Scripts\activate
start python main.py
deactivate
cd ..

echo Starting frontend...
cd frontend
start "Frontend Server" npm run dev
cd ..

timeout /t 5 /nobreak >nul
echo Opening application in browser...
start http://localhost:8000

echo Application is running!
echo Backend: http://localhost:7000
echo Frontend: http://localhost:8000
pause