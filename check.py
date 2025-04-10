import os
import platform
import subprocess
from colorama import Fore, Style
def requirement_checker():

    print("Checking if required software and virtual environment are installed...")
    if platform.system() == "Windows":
        required_software = ["winget", "npm", "python", "ollama"]
    elif platform.system() == "Linux":
        required_software = ["npm", "python3", "ollama"]
    else:
        print("Unsupported operating system. Skipping requirement check.")
        return

    for software in required_software:
        try:
            subprocess.run([software, "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{software} is installed.")
        except FileNotFoundError:
            print(f"{Fore.RED}{software} is not installed. Please install it and try again.{Style.RESET_ALL}")

    # Check if virtual environment exists
    venv_path = os.path.join(os.getcwd(), "venv")
    if os.path.exists(venv_path):
        print("Virtual environment exists.")
    else:
        print(f"{Fore.RED}Virtual environment does not exist. Please create it and try again.{Style.RESET_ALL}")

requirement_checker()