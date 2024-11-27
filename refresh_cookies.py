import os
import subprocess
import time

def refresh_cookies():
    cookies_path = "cookies.txt"  # Update with the path your backend uses
    command = f'yt-dlp --cookies-from-browser edge --cookies {cookies_path}'  # Adjust "edge" for your browser
    try:
        print("Refreshing cookies...")
        subprocess.run(command, shell=True, check=True)
        print("Cookies refreshed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to refresh cookies: {e}")

if __name__ == "__main__":
    while True:
        refresh_cookies()
        time.sleep(15 * 60)  # Wait for 15 minutes before refreshing again
