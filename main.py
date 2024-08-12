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

# Health detection
def check_health():
    # Capture the health bar region
    health_bar_region = (100, 200, 150, 20)  # Adjust the region to the health bar location
    health_before = capture_screen(health_bar_region)
    
    # Convert to grayscale and threshold
    gray_health = cv2.cvtColor(health_before, cv2.COLOR_BGR2GRAY)
    _, thresh_health = cv2.threshold(gray_health, 200, 255, cv2.THRESH_BINARY)

    # Find contours of the health bar
    contours, _ = cv2.findContours(thresh_health, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    health_area = sum(cv2.contourArea(c) for c in contours)
    
    # Calculate health percentage
    health_percentage = (health_area / 10000) * 100  # Assuming the full bar is 10000 pixels in area, adjust if necessary

    log(f"Health percentage: {health_percentage}%")

    return health_percentage < 50

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
        self.machine.add_transition(trigger='heal', source='attacking', dest='healing', conditions='check_health')
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
                if check_health():
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

# Main entry point
if __name__ == "__main__":
    bot = WoWBot()
    bot.run()