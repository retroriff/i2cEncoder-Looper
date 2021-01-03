# GPIO Button Test
from gpiozero import Button
buttons_gpio  = [13, 19, 26, 11, 5, 6, 9, 10, 17, 22, 27]
button_gpio   = []

# Fails 0
button_number = 0
button        = Button( buttons_gpio[button_number] )
button_status = False

# button_gpio.append( Button( 19 ) )

for idx, value in enumerate(buttons_gpio):
    print buttons_gpio[idx]
    # button_gpio.insert( Button( buttons_gpio[button_number] ) )

while True:
    if button.is_pressed:
        if button_status == False:
            print "Button " + str(button_number) + " is pressed"
            button_status = True
    else:
        if button_status == True:
            print "Button " + str(button_number) + " is not pressed"
            button_status = False