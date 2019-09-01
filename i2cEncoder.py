# I2CEncoderV2
# Library: https://github.com/Fattoresaimon/I2CEncoderV2/blob/master/Raspberry%20Library/smbus2/i2cEncoderLibV2.py
# Date: 2019/05/17
# Author: https://github.com/retroriff

import random
from itertools import cycle
import argparse
import os

import smbus2
from gpiozero import Button
import i2cEncoderLibV2
from pythonosc import udp_client
from pythonosc import osc_message_builder


print('Running Samplemàtic on the {}'.format(os.uname()[1].capitalize()))

MIN_VAL, MAX_VAL = 0, 20
DEVICES = [
    [0x21, 0x5, 0x41, 0x9, 0x40],
    [0x11, 0x20, 0x3],
]
int_pin = Button(4)
osc_address_patterns = ["/switch", "/amp", "/rate", "/start", "/length"]
osc_address_patterns_alt = ["/attach", "/pitch"]

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
    encoder.writeCounter(int(MAX_VAL / 2))  # Debug Python3: preguntar a Marc
    encoder.writeMax(MAX_VAL)
    encoder.writeMin(MIN_VAL)
    encoder.writeStep(1)
    encoder.writeInterruptConfig(0xff)

    return encoder


parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1",
                    help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=57120,
                    help="The port the OSC server is listening on")
args = parser.parse_args()
#client = udp_client.SimpleUDPClient(args.ip, args.port)
client = udp_client.SimpleUDPClient("192.168.8.100", args.port)


def send_msg(address, channel, value):
    msg = osc_message_builder.OscMessageBuilder(address=address)
    msg.add_arg(channel, arg_type='i')
    msg.add_arg(value, arg_type='i')
    msg = msg.build()
    client.send(msg)


def run_encoder(encoder):
    EXP_GROWTH = 3
    counter = encoder.readCounter32()
    # Default colors values
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
        encoder.writeRGBCode(int(color, 0))
        send_msg(osc_address_patterns[idx], channel, counter)
        print('{} {} {} ({}, {})'.format(osc_address_patterns[idx], channel, counter, printColor, color))


encoders = []
for idx, channel in enumerate(DEVICES):
    encoders.append([])
    for value in channel:
        encoders[idx].append(init_encoder(value))

try:
    for channel, row in cycle(enumerate(encoders)):
        for idx, encoder in enumerate(row):
            # Play: if int_pin.is_pressed:
            encoder.updateStatus()

            # Encoder turns right
            if encoder.readStatus(i2cEncoderLibV2.RINC):
                run_encoder(encoder)

            # Encoder turns left
            if encoder.readStatus(i2cEncoderLibV2.RDEC):
                run_encoder(encoder)

            # Encoder pushed
            if encoder.readStatus(i2cEncoderLibV2.PUSHP):
                print("Click")
                encoder.writeCounter(random.randint(MIN_VAL, MAX_VAL))
                run_encoder(encoder)


except KeyboardInterrupt:
    for _, row in enumerate(encoders):
        for encoder in row:
            encoder.writeRGBCode(0)
