import time

def log(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def wait(seconds):
    time.sleep(seconds)
