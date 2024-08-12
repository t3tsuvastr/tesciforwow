import pyautogui
import cv2
import numpy as np
import time
from transitions import Machine

# Utility functions (can be moved to utils.py if desired)
def log(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def wait(seconds):
    time.sleep(seconds)

# Game interaction functions
def capture_screen():
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

def find_template(template_path):
    screen = capture_screen()
    template = cv2.imread(template_path, 0)
    res = cv2.matchTemplate(cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY), template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    return loc[0].size > 0

def press_key(key):
    pyautogui.press(key)

# Bot states and logic
class WoWBot:
    states = ['idle', 'searching', 'attacking']

    def __init__(self):
        self.machine = Machine(model=self, states=WoWBot.states, initial='idle')
        self.machine.add_transition(trigger='find_mob', source='idle', dest='searching')
        self.machine.add_transition(trigger='attack_mob', source='searching', dest='attacking')
        self.machine.add_transition(trigger='reset', source='attacking', dest='idle')

    def run(self):
        while True:
            if self.state == 'idle':
                log("Bot is idle...")
                self.find_mob()
            elif self.state == 'searching':
                log("Searching for mobs...")
                if self.detect_mob():
                    self.attack_mob()
            elif self.state == 'attacking':
                log("Attacking the mob...")
                self.attack()
                self.reset()
            wait(1)

    def detect_mob(self):
        # Placeholder for mob detection logic
        return True  # Change this with actual detection logic

    def attack(self):
        press_key('1')  # Example attack

# Main entry point
if __name__ == "__main__":
    bot = WoWBot()
    bot.run()
