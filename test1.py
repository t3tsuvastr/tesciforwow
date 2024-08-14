import cv2
import numpy as np
import pyautogui
import time

# Define the region where the HP bar appears (using the exact coordinates)
hp_bar_region = (1570, 1010, 225, 25)

# Utility function to capture the screen
def capture_screen(region=None):
    screenshot = pyautogui.screenshot(region=region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

# Function to log messages with timestamps
def log(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

# Function to detect the HP bar
def detect_hp_bar():
    while True:
        # Capture the screen in the defined region
        screen_capture = capture_screen(region=hp_bar_region)
        
        # Convert to HSV color space
        hsv_capture = cv2.cvtColor(screen_capture, cv2.COLOR_BGR2HSV)
        
        # Define the green color range for the HP bar in HSV
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        
        # Create a mask for the green color
        mask_green = cv2.inRange(hsv_capture, lower_green, upper_green)
        
        # Calculate the area of the green part (HP bar)
        green_area = np.sum(mask_green == 255)
        
        # If green area is above a certain threshold, the HP bar is present
        if green_area > 0:
            log("HP bar detected!")
        else:
            log("HP bar not detected.")
        
        # Pause briefly before the next check
        time.sleep(0.5)

# Main entry point to start the detection
if __name__ == "__main__":
    detect_hp_bar()
