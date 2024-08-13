import pyautogui
import time
import cv2
import numpy as np
from transitions import Machine
from threading import Thread
import keyboard

class WoWBot:
    states = ['idle', 'scanning', 'targeting', 'attacking', 'looting']

    def __init__(self):
        self.machine = Machine(model=self, states=WoWBot.states, initial='idle')
        self.machine.add_transition(trigger='scan_for_enemies', source='idle', dest='scanning')
        self.machine.add_transition(trigger='target_enemy', source='scanning', dest='targeting')
        self.machine.add_transition(trigger='attack_enemy', source='targeting', dest='attacking')
        self.machine.add_transition(trigger='loot_enemy', source='attacking', dest='looting')
        self.machine.add_transition(trigger='reset_to_idle', source='*', dest='idle')
        self.stop_bot = False

    def run(self):
        def listen_for_stop():
            while True:
                if keyboard.is_pressed('\\'):
                    print("Stopping bot...")
                    self.stop_bot = True
                    break

        stop_thread = Thread(target=listen_for_stop)
        stop_thread.start()

        while not self.stop_bot:
            if self.state == 'idle':
                self.scan_for_enemies()
            elif self.state == 'scanning':
                if self.detect_enemy():
                    self.target_enemy()
                else:
                    self.reset_to_idle()
            elif self.state == 'targeting':
                if self.is_enemy_targeted():
                    self.attack_enemy()
                else:
                    self.reset_to_idle()
            elif self.state == 'attacking':
                if self.is_enemy_dead():
                    self.loot_enemy()
                else:
                    self.reset_to_idle()
            elif self.state == 'looting':
                self.reset_to_idle()
            time.sleep(0.1)  # Small delay to prevent excessive CPU usage

        stop_thread.join()

    def detect_enemy(self):
        print("[DEBUG] Detecting enemy...")
        # Capture the screen
        screen = self.capture_screen()
        
        # Convert the screenshot to grayscale
        gray_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        
        # Use a basic threshold to identify red borders around enemies
        _, thresh = cv2.threshold(gray_screen, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours that may represent the red border of the enemy's HP bar
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            # Assume the red border is a rectangle within a specific size range
            if 30 < w < 150 and 10 < h < 50:
                center_x, center_y = x + w // 2, y + h // 2
                print(f"[DEBUG] Enemy detected at ({center_x}, {center_y})")
                self.move_camera(center_x - 960, center_y - 540)  # Centering the detected enemy
                return True
        
        return False

    def is_enemy_targeted(self):
        print("[DEBUG] Checking if enemy is targeted...")
        # Check if the red HP bar is locked on the bottom of the screen
        screen_region = (1500, 850, 400, 200)  # Adjust these coordinates based on your screen resolution
        screen = self.capture_screen(screen_region)
        hsv_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv_screen, lower_red, upper_red)
        
        if np.sum(mask) > 0:
            print("[DEBUG] Target confirmed.")
            return True
        
        print("[DEBUG] No target found.")
        return False

    def is_enemy_dead(self):
        print("[DEBUG] Checking if enemy is dead...")
        # Implement logic to check if the enemy is dead
        time.sleep(1)
        return True

    def move_camera(self, dx, dy, duration=0.5):
        self.hold_right_mouse_button()
        pyautogui.moveRel(dx * 0.2, dy * 0.2, duration=duration)
        self.release_right_mouse_button()

    def hold_right_mouse_button(self):
        pyautogui.mouseDown(button='right')

    def release_right_mouse_button(self):
        pyautogui.mouseUp(button='right')

    def capture_screen(self, region=None):
        screenshot = pyautogui.screenshot(region=region)
        screen = np.array(screenshot)
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        return screen

    def loot_enemy(self):
        print("[DEBUG] Looting enemy...")
        time.sleep(1)
        self.reset_to_idle()

# Instantiate and run the bot
if __name__ == "__main__":
    bot = WoWBot()
    bot.run()
