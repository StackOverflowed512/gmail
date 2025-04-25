#!/bin/bash
echo "Starting backend..."
cd backend
source venv/bin/activate
python main.py &
deactivate
cd ..

echo "Starting frontend..."
cd frontend
npm run dev &
cd ..

# Wait for server to start then open browser
sleep 5
echo "Opening application in browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8000
else
    xdg-open http://localhost:8000
fi

echo "Application is running!"
echo "Backend: http://localhost:7000"
echo "Frontend: http://localhost:8000"