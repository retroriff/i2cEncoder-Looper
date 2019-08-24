# I2CEncoderV2
# Library: https://github.com/Fattoresaimon/I2CEncoderV2/blob/master/Raspberry%20Library/smbus2/i2cEncoderLibV2.py
# Date: 2019/05/17
# Author: https://github.com/retroriff

import random
from itertools import cycle

import smbus2
from gpiozero import Button
import i2cEncoderLibV2
#from pythonosc import udp_client
import argparse



MIN_VAL, MAX_VAL = 0, 10.0
DEVICES = [
    [0x21, 0x5, 0x41, 0x9, 0x40],
    [0x11, 0x20, 0x3],
]
int_pin = Button(4)

def init_encoder(device):
    bus = smbus2.SMBus(1)
    encoder = i2cEncoderLibV2.i2cEncoderLibV2(bus, device)

    encconfig = (i2cEncoderLibV2.INT_DATA |
                 i2cEncoderLibV2.WRAP_DISABLE |
                 i2cEncoderLibV2.DIRE_RIGHT |
                 i2cEncoderLibV2.IPUP_ENABLE |
                 i2cEncoderLibV2.RMOD_X1 |
                 i2cEncoderLibV2.RGB_ENCODER)
    encoder.begin(encconfig)
    encoder.writeCounter(MAX_VAL/2)
    encoder.writeMax(MAX_VAL)
    encoder.writeMin(MIN_VAL)
    encoder.writeStep(1)
    encoder.writeInterruptConfig(0xff)

    return encoder

def change_color(encoder):
    EXP_GROWTH = 3
    counter = encoder.readCounter32()
    # Default values
    color = '0x00'
    printColor = "Off"

    # Set color Red
    if counter > MAX_VAL / 2:
        color_step = (MAX_VAL - counter + 1) ** EXP_GROWTH
        color = '0x{:02x}0000'.format(int(255 / color_step))
        printColor = "Red"

    # Set color Blue
    if counter < MAX_VAL / 2:
        colorStep = counter + 1 ** EXP_GROWTH 
        color = '0x0000{:02x}'.format(int(255 / colorStep))
        printColor = "Blue"

    if (not encoder.readStatus(i2cEncoderLibV2.RMAX) and
            not encoder.readStatus(i2cEncoderLibV2.RMIN)):
        encoder.writeRGBCode(0)
        print('Counter: {} {}: {}'.format(counter, printColor, color))


encoders = []
for idx, channel in enumerate(DEVICES):
    encoders.append([])
    for value in channel:
        print(idx)
        encoders[idx].append(init_encoder(value))


# try: 
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--sp", default = "192.168.8.100", help = "SuperCollider server is on")
#     parser.add_argument("--port", type = int, default = 4559, help = "The port to listen on")
#     args = parser.parse_args()
#     ip = args.sp
#     print("Looper running on remote_host:", spip, "Port:", args.port)
#     client = udp_client.SimpleUDPClient(spip, args.port)
# except AttributeError as err:
#     print(err.args[0])
# except OSError as err:
#     print("OSC server error",err.args)


try:
    for channel, row in enumerate(cycle(encoders)):
        for encoder in row:
            # Play: if int_pin.is_pressed:
            encoder.updateStatus()

            # Encoder turns right
            if encoder.readStatus(i2cEncoderLibV2.RINC):
                change_color(encoder)

            # Encoder turns left
            if encoder.readStatus(i2cEncoderLibV2.RDEC):
                change_color(encoder)
            
            # Encoder pushed
            if encoder.readStatus(i2cEncoderLibV2.PUSHP):
                print("Click")
                encoder.writeCounter(random.randint(MIN_VAL, MAX_VAL))
                change_color(encoder)


except KeyboardInterrupt:
    for _, row in enumerate(encoders):
        for encoder in row:
            encoder.writeRGBCode(0)