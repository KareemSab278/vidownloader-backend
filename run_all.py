import subprocess
import threading

def start_backend():
    subprocess.run("python backend.py", shell=True)

def refresh_cookies():
    subprocess.run("python refresh_cookies.py", shell=True)

if __name__ == "__main__":
    threading.Thread(target=start_backend).start()
    threading.Thread(target=refresh_cookies).start()
