import pyautogui
import cv2
import numpy as np
import time
import random
from transitions import Machine

# Utility functions
def log(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def wait(seconds):
    time.sleep(seconds)

# Game interaction functions
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

def loot():
    pyautogui.moveTo(960, 540)  # Move cursor to the center of the screen (assumes loot is in the center)
    right_click()

# Bot states and logic
class WoWBot:
    states = ['idle', 'moving', 'targeting', 'attacking', 'healing', 'looting']

    def __init__(self):
        self.machine = Machine(model=self, states=WoWBot.states, initial='idle')
        self.machine.add_transition(trigger='move_to_target', source='idle', dest='moving')
        self.machine.add_transition(trigger='target_enemy', source='moving', dest='targeting')
        self.machine.add_transition(trigger='attack_target', source='targeting', dest='attacking')
        self.machine.add_transition(trigger='heal', source='attacking', dest='healing', conditions=['check_health'])
        self.machine.add_transition(trigger='loot_corpse', source='attacking', dest='looting')
        self.machine.add_transition(trigger='reset', source=['healing', 'looting'], dest='idle')

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
                self.attack_target()
            elif self.state == 'attacking':
                log("Attacking the mob...")
                spell_key = str(random.randint(1, 5))  # Randomly select spell 1-5
                press_key(spell_key)
                if self.check_health():
                    self.heal()
                else:
                    # Assuming the mob is killed after attack
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

    def check_health(self):
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

# Main entry point
if __name__ == "__main__":
    bot = WoWBot()
    bot.run()
