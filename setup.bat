@echo off
echo Pulling Ollama model...
ollama pull mistral:7b-instruct-q4_K_M

echo Setting up backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..

echo Setting up frontend...
cd frontend
npm install
cd ..

echo Setup completed successfully!
pause