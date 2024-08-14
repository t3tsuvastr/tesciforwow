import pyautogui
import cv2
import numpy as np
import time
import random
from transitions import Machine

# Define the region where the HP bar appears (exact coordinates)
hp_bar_region = (1570, 1010, 225, 25)

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

def move_forward():
    pyautogui.keyDown('w')
    wait(0.5)
    pyautogui.keyUp('w')

def cycle_targets():
    pyautogui.press('tab')

# Function to detect the HP bar
def detect_hp_bar():
    screen_capture = capture_screen(region=hp_bar_region)
    hsv_capture = cv2.cvtColor(screen_capture, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    mask_green = cv2.inRange(hsv_capture, lower_green, upper_green)
    green_area = np.sum(mask_green == 255)
    return green_area > 0

# Bot states and logic
class WoWBot:
    states = ['idle', 'moving', 'targeting', 'attacking', 'healing']

    def __init__(self):
        self.machine = Machine(model=self, states=WoWBot.states, initial='idle')
        self.machine.add_transition(trigger='move_to_target', source='idle', dest='moving')
        self.machine.add_transition(trigger='target_enemy', source='moving', dest='targeting')
        self.machine.add_transition(trigger='attack_target', source='targeting', dest='attacking', conditions=['detect_hp_bar'])
        self.machine.add_transition(trigger='heal', source='attacking', dest='healing', conditions=['check_health'])
        self.machine.add_transition(trigger='reset', source=['healing'], dest='idle')

    def run(self):
        while True:
            if self.state == 'idle':
                log("Bot is idle...")
                self.move_to_target()
            elif self.state == 'moving':
                log("Moving towards target...")
                move_forward()
                self.target_enemy()
            elif self.state == 'targeting':
                log("Targeting the mob...")
                cycle_targets()
                if self.detect_hp_bar():
                    self.attack_target()
                else:
                    log("HP bar not detected. Retargeting...")
                    cycle_targets()  # Try targeting another enemy
            elif self.state == 'attacking':
                log("Attacking the mob...")
                spell_key = str(random.randint(1, 5))  # Randomly select spell 1-5
                press_key(spell_key)
                if self.check_health():
                    self.heal()
                else:
                    log("Attack completed. Returning to idle state.")
                    self.reset()
            elif self.state == 'healing':
                log("Healing...")
                press_key('6')
                self.reset()
            wait(1)

    def check_health(self):
        # Dummy health check function (replace with actual logic)
        return False

if __name__ == "__main__":
    bot = WoWBot()
    bot.run()

print('nohting')