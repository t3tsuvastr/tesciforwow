import pyautogui
import cv2
import numpy as np
import time
import random
import threading
import sys
from transitions import Machine

# Utility functions
def log(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def wait(seconds):
    time.sleep(seconds)

def capture_screen(region=None):
    screenshot = pyautogui.screenshot(region=region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

def press_key(key):
    pyautogui.press(key)

def right_click():
    pyautogui.click(button='right')

def hold_right_mouse_button():
    pyautogui.mouseDown(button='right')

def release_right_mouse_button():
    pyautogui.mouseUp(button='right')

def move_camera(dx, dy, duration=0.2):
    pyautogui.moveRel(dx, dy, duration=duration)

def move_forward(duration=0.5):
    pyautogui.keyDown('w')
    wait(duration)
    pyautogui.keyUp('w')

def cycle_targets():
    pyautogui.press('tab')

def loot():
    pyautogui.moveTo(960, 540)  # Move cursor to the center of the screen (assumes loot is in the center)
    right_click()

def detect_enemy():
    # Capture the full screen
    screen = capture_screen()
    
    # Convert the screen capture to HSV color space
    hsv_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
    
    # Define the range of the red color (used in enemy names and health bars)
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    
    # Create a mask to capture red areas on the screen
    mask_red = cv2.inRange(hsv_screen, lower_red, upper_red)
    
    # Find contours of the red areas
    contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Get the largest contour which is likely to be the enemy
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get the bounding box of the contour
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Calculate the center of the detected area
        center_x = x + w // 2
        center_y = y + h // 2
        
        log(f"Enemy detected at ({center_x}, {center_y})")
        
        # Move the camera to the detected enemy (center of the red area)
        hold_right_mouse_button()
        move_camera(center_x - 960, center_y - 540)  # Centering the detected enemy
        release_right_mouse_button()
        
        return True
    else:
        log("No enemies detected")
        return False

def confirm_target():
    # Region where the red border and HP bar appear
    screen_region = (1500, 875, 275, 70)  # Accurate coordinates based on the screenshot
    screen = capture_screen(screen_region)
    
    # Convert to HSV and create a mask for red color
    hsv_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    mask_red = cv2.inRange(hsv_screen, lower_red, upper_red)
    
    # Check if red border and health bar are detected
    red_area = np.sum(mask_red == 255)
    if red_area > 1000:  # Threshold for detection
        log("Target confirmed with red border and HP bar")
        return True
    else:
        log("Target not confirmed")
        return False

def check_health():
    # Region of interest for the health bar based on detected coordinates
    health_bar_region = (308, 651, 268, 114)  # Coordinates: x, y, width, height
    
    log(f"Checking health in region: {health_bar_region}")
    health_before = capture_screen(health_bar_region)
    
    # Convert the health bar region to HSV color space to better isolate the green color
    hsv_health = cv2.cvtColor(health_before, cv2.COLOR_BGR2HSV)
    
    # Define the range of the green color in HSV
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    
    # Create a mask that captures only the green color
    mask_green = cv2.inRange(hsv_health, lower_green, upper_green)
    
    # Calculate the area of the green part (health bar)
    green_area = np.sum(mask_green == 255)
    
    # Calculate the health percentage based on the area of the green bar
    total_area = 268 * 114  # Total area of the health bar region
    health_percentage = (green_area / total_area) * 100
    
    log(f"Health percentage: {health_percentage}%")

    # Heal if health is below 50%
    return health_percentage < 50

def position_camera_for_loot():
    log("Positioning camera for loot...")
    # A small forward movement to align with the lootable body
    move_forward(duration=0.3)
    # Hold the right mouse button to adjust the camera angle
    hold_right_mouse_button()
    move_camera(0, 50)  # Slight downward movement to ensure the body is in view
    release_right_mouse_button()

# Function to listen for the stop signal
def stop_bot_listener(bot):
    while True:
        user_input = input("Press \\ to stop the bot: ")
        if user_input == "\\":
            log("Stop signal received. Stopping the bot...")
            bot.stop()
            sys.exit()

# Bot states and logic
class WoWBot:
    states = ['idle', 'scanning', 'targeting', 'attacking', 'healing', 'looting']

    def __init__(self):
        self.machine = Machine(model=self, states=WoWBot.states, initial='idle')
        self.machine.add_transition(trigger='scan_for_enemies', source='idle', dest='scanning')
        self.machine.add_transition(trigger='target_enemy', source='scanning', dest='targeting', conditions=['detect_enemy'])
        self.machine.add_transition(trigger='attack_target', source='targeting', dest='attacking')
        self.machine.add_transition(trigger='heal', source='attacking', dest='healing', conditions=['check_health'])
        self.machine.add_transition(trigger='loot_corpse', source='attacking', dest='looting')
        self.machine.add_transition(trigger='reset', source=['healing', 'looting'], dest='idle')

    def run(self):
        while True:
            if self.state == 'idle':
                log("Bot is idle...")
                self.scan_for_enemies()
            elif self.state == 'scanning':
                log("Scanning for enemies...")
                if self.detect_enemy():
                    self.target_enemy()
            elif self.state == 'targeting':
                log("Targeting the mob...")
                if self.confirm_target():
                    self.attack_target()
                else:
                    log("Target not confirmed, retrying...")
                    self.scan_for_enemies()
            elif self.state == 'attacking':
                log("Attacking the mob...")
                spell_key = str(random.randint(1, 5))  # Randomly select spell 1-5
                press_key(spell_key)
                if self.check_health():
                    self.heal()
                else:
                    # Assuming the mob is killed after attack
                    self.position_camera_for_loot()
                    self.loot_corpse()
            elif self.state == 'healing':
                log("Healing...")
                press_key('6')
                self.reset()
            elif self.state == 'looting':
                log("Looting the corpse...")
                loot()
                self.reset()
            wait(1)

    def stop(self):
        log("Bot has stopped.")

if __name__ == "__main__":
    bot = WoWBot()
    
    # Start the stop listener in a separate thread
    stop_thread = threading.Thread(target=stop_bot_listener, args=(bot,))
    stop_thread.daemon = True
    stop_thread.start()
    
    # Run the bot
    bot.run()