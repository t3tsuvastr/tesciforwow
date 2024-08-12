import pyautogui
import cv2
import numpy as np
import time
from transitions import Machine

# служебные функции (импорт-е из utils.py)утилиты короче говоря
def log(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def wait(seconds):
    time.sleep(seconds)

# функции взаимодействия с игрой
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

def right_click():
    pyautogui.click(button='right')

def move_forward():
    pyautogui.keyDown('w')
    wait(0.5)
    pyautogui.keyUp('w')

# состояние и логика бота
class TestTfaiBot:
    states = ['idle', 'moving', 'targeting', 'attacking']

    def __init__(self):
        self.machine = Machine(model=self, states=TestTfaiBot.states, initial='idle')
        self.machine.add_transition(trigger='move_to_target', source='idle', dest='moving')
        self.machine.add_transition(trigger='target_enemy', source='moving', dest='targeting')
        self.machine.add_transition(trigger='attack_target', source='targeting', dest='attacking')
        self.machine.add_transition(trigger='reset', source='attacking', dest='idle')

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
                right_click()  # авто атака
                self.attack_target()
            elif self.state == 'attacking':
                log("Attacking the mob...")
                press_key('1')  # нужно здесь добавить атаки которые имеются в вовке
                self.reset()
            wait(1)

#  мэйн вход
if __name__ == "__main__":
    bot = TestTfaiBot()
    bot.run()