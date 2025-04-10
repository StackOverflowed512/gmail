import os
import platform
import subprocess
import threading
import socket
import webbrowser

def install_setup():
    system = platform.system()
    if system == "Linux":
        print("Detected Linux. Installing Node.js...")
        os.system("sudo apt update && sudo apt install -y nodejs npm")
    elif system == "Windows":
        print("Detected Windows. Checking if Node.js is installed...")
        try:
            subprocess.run(["npm", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Node.js is already installed.")
        except subprocess.CalledProcessError:
            print("Node.js is not installed. Installing Node.js using winget...")
            subprocess.run(["winget", "install", "Schniz.fnm"], shell=True)  # fnm install 22
            subprocess.run(["fnm", "install", "22"], shell=True)
            print("Node.js installation complete.")
    else:
        print("Unsupported operating system: {system}")
    venv_path = os.path.join(os.getcwd(), "venv")
    if not os.path.exists(venv_path):
        print("Creating virtual environment...")
        subprocess.run(["python3", "-m", "venv", "venv"])
        print("Virtual environment created.")
    else:
        print("Virtual environment already exists.")
        requirements_file = os.path.join(os.getcwd(), "requirments.txt")
        if os.path.exists(requirements_file):
            print("Installing packages from requirements.txt...")
            subprocess.run(["venv/bin/pip", "install", "-r", "requirments.txt"])
            print("Packages installed successfully.")
        else:
            print("requirements.txt not found. Skipping package installation.")
    frontend_path = os.path.join(os.getcwd(), "frontend")
    node_modules_path = os.path.join(frontend_path, "node_modules")
    if os.path.exists(frontend_path):
        if os.path.exists(node_modules_path):
            print("node_modules folder already exists in the 'frontend' directory.")
        else:
            print("node_modules folder not found in the 'frontend' directory. Installing dependencies...")
            subprocess.run(["npm", "install"], cwd=frontend_path)
            print("Dependencies installed successfully.")
    else:
        print("'frontend' directory not found. Skipping node_modules check.")
    # Check if 'wolama' command is working
    try:
        subprocess.run(["ollama s", "-v"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("'ollama' command is working.")
        print("Pulling 'mistral' model using 'ollama'...")
        subprocess.run(["ollama", "pull", "mistral"], check=True)
        print("'muscle' model installed successfully.")
    except FileNotFoundError:
        print("'ollama' command is not found. Redirecting to the Olama download")
        webbrowser.open("https://ollama.com/download/OllamaSetup.exe")
        print("Please install 'ollama' manually and then run this script again.")
        exit(1)
    except subprocess.CalledProcessError:
        print("'ollama' command is not working correctly. Please check your installation.")
    # Start the frontend server
    frontend_path = os.path.join(os.getcwd(), "frontend")
    def is_port_free(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0

    def free_port(port):
        try:
            if platform.system() == "Linux":
                subprocess.run(["fuser", "-k", f"{port}/tcp"], check=True)
            elif platform.system() == "Windows":
                subprocess.run(["netstat", "-ano", "|", "findstr", f":{port}"], shell=True)
                subprocess.run(["taskkill", "/F", "/PID", f"{port}"], shell=True)
            print(f"Port {port} has been freed.")
        except subprocess.CalledProcessError:
            print(f"Failed to free port {port}. Please check manually.")

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
    url = "http://localhost:8000" 
    webbrowser.open(url)


