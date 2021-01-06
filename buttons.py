# GPIO Button Test
from itertools import cycle
from gpiozero import Button


def load_buttons():
    buttons_gpio = [13, 19, 26, 11, 5, 6, 9, 10, 17, 22, 27]

    return [Button(b_num) for b_num in buttons_gpio]


if __name__ == "__main__":
    buttons = load_buttons()
    button_status = [False] * 11
    i = 0

    for button in cycle(buttons):
        if button.is_pressed:
            if button_status[i] == False:
                print("button " + str(button.pin) + " pressed")
                button_status[i] = True
        else:
            if button_status[i] == True:
                print("button " + str(button.pin) + " unpressed")
                button_status[i] = False

        if i >= 10:
            i = 0
        else: 
            i = i + 1

