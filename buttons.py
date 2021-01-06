# GPIO Button Test
import time
from itertools import cycle
from gpiozero import Button


def load_buttons():
    buttons_gpio = [13, 19, 26, 11, 5, 6, 9, 10, 17, 22, 27]

    return [Button(b_num) for b_num in buttons_gpio]


if __name__ == "__main__":
    buttons = load_buttons()
    button_status = [False] * len(buttons)

    for i, button in (enumerate(cycle(buttons)):
        idx = i % len(buttons)
        if button.is_pressed and button_status[idx] is False:
            print("button " + str(button.pin) + " pressed")
            button_status[idx] = True

        elif button_status[idx] is True:
            print("button " + str(button.pin) + " unpressed")
            button_status[idx] = False

        time.sleep(0.1)
