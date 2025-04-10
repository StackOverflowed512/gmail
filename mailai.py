import os
import platform
import subprocess
import threading
def start_backend():
    backend_path = os.path.join(os.getcwd(), "backend")
    main_py_path = os.path.join(backend_path, "main.py")
    if os.path.exists(main_py_path):
        if not is_port_free(7000):
            print("Port 7000 is in use. Attempting to free it...")
            free_port(7000)
        print("Starting the backend server...")
        if platform.system() == "Linux":
            subprocess.Popen(["gnome-terminal", "--", "python3", main_py_path], cwd=backend_path)
        elif platform.system() == "Windows":
            subprocess.Popen(["start", "cmd", "/k", "python", main_py_path], shell=True, cwd=backend_path)
        print("Backend server started.")
    else:
        print("'main.py' not found in the 'backend' directory. Skipping backend server startup.")

def start_frontend():
    if os.path.exists(frontend_path):
        print("Starting the frontend server...")
        if platform.system() == "Linux":
            subprocess.Popen(["gnome-terminal", "--", "npm", "run", "build"], cwd=frontend_path)
            subprocess.Popen(["gnome-terminal", "--", "npm", "start"], cwd=frontend_path)
        elif platform.system() == "Windows":
            subprocess.Popen(["start", "cmd", "/k", "npm run build"], shell=True, cwd=frontend_path)
            subprocess.Popen(["start", "cmd", "/k", "npm start"], shell=True, cwd=frontend_path)
        print("Frontend server started.")
    else:
        print("'frontend' directory not found. Skipping frontend server startup.")

backend_thread = threading.Thread(target=start_backend)
frontend_thread = threading.Thread(target=start_frontend)
backend_thread.start()
backend_thread.join()
frontend_thread.start()