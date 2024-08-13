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

def move_camera(dx, dy, duration=0.5):
    pyautogui.moveRel(dx, dy, duration=duration)

def move_forward(duration=0.5):
    pyautogui.keyDown('w')
    wait(duration)
    pyautogui.keyUp('w')

def cycle_targets():
    pyautogui.press('tab')

def loot():
    pyautogui.moveTo(960, 540)
    right_click()

def check_health():
    health_bar_region = (308, 651, 268, 114)
    
    log(f"Checking health in region: {health_bar_region}")
    health_before = capture_screen(health_bar_region)
    
    hsv_health = cv2.cvtColor(health_before, cv2.COLOR_BGR2HSV)
    
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    
    mask_green = cv2.inRange(hsv_health, lower_green, upper_green)
    
    green_area = np.sum(mask_green == 255)
    
    total_area = 268 * 114
    health_percentage = (green_area / total_area) * 100
    
    log(f"Health percentage: {health_percentage}%")

    return health_percentage < 50

def position_camera_for_loot():
    log("Positioning camera for loot...")
    move_forward(duration=0.3)
    hold_right_mouse_button()
    move_camera(0, 50)
    release_right_mouse_button()

def stop_bot_listener(bot):
    while True:
        user_input = input("Press \\ to stop the bot: ")
        if user_input == "\\":
            log("Stop signal received. Stopping the bot...")
            bot.stop()
            sys.exit()

class WoWBot:
    states = ['idle', 'scanning', 'targeting', 'attacking', 'healing', 'looting']

    def __init__(self):
        self.machine = Machine(model=self, states=WoWBot.states, initial='idle')
        self.machine.add_transition(trigger='scan_for_enemies', source='idle', dest='scanning')
        self.machine.add_transition(trigger='target_enemy', source='scanning', dest='targeting', conditions=['detect_enemy'])
        self.machine.add_transition(trigger='attack_target', source='targeting', dest='attacking')
        self.machine.add_transition(trigger='heal', source='attacking', dest='healing', conditions=['check_health'])
        self.machine.add_transition(trigger='loot_corpse', source='attacking', dest='looting')
        self.machine.add_transition(trigger='reset', source=['healing', 'looting', 'targeting'], dest='idle')

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
                    self.reset()  # Reset to idle state to scan again
            elif self.state == 'attacking':
                log("Attacking the mob...")
                spell_key = str(random.randint(1, 5))
                press_key(spell_key)
                if self.check_health():
                    self.heal()
                else:
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

    def detect_enemy(self):
        screen = capture_screen()

        hsv_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)

        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])

        mask_red = cv2.inRange(hsv_screen, lower_red, upper_red)

        contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)

            center_x = x + w // 2
            center_y = y + h // 2

            log(f"Enemy detected at ({center_x}, {center_y})")

            hold_right_mouse_button()

            move_camera((center_x - 960) * 0.5, (center_y - 540) * 0.5)
            wait(0.1)
            move_camera((center_x - 960) * 0.5, (center_y - 540) * 0.5)

            release_right_mouse_button()

            return True
        else:
            log("No enemies detected")
            return False

    def confirm_target(self):
        screen_region = (1520, 860, 300, 80)
        screen = capture_screen(screen_region)

        hsv_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask_red = cv2.inRange(hsv_screen, lower_red, upper_red)

        red_area = np.sum(mask_red == 255)
        if red_area > 1000:
            log("Target confirmed with red border and HP bar")
            return True
        else:
            log("Target not confirmed")
            return False

    def stop(self):
        log("Bot has stopped.")

if __name__ == "__main__":
    bot = WoWBot()

    stop_thread = threading.Thread(target=stop_bot_listener, args=(bot,))
    stop_thread.daemon = True
    stop_thread.start()

    bot.run()