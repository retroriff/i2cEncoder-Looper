# GPIO Button Test
from itertools import cycle
from gpiozero import Button


def load_buttons():
    buttons_gpio = [13, 19, 26, 11, 5, 6, 9, 10, 17, 22, 27]

    return [Button(b_num) for b_num in buttons_gpio]


if __name__ == "__main__":
    buttons = load_buttons()

    for button in cycle(buttons):
        if button.is_pressed:
            print(f"Button {button.pin} is pressed")
