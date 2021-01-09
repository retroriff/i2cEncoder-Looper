# I2C Encoders and Buttons Messages to SuperCollider
# Description: Send OSC Messages with I2C Encoders V2 and buttons from Raspberry Pi's GPIO to SuperCollider
# Author: https://github.com/retroriff/I2CEncoderV2-Looper
# Date: 2019/05/17
# Library: https://github.com/Fattoresaimon/I2CEncoderV2/blob/master/Raspberry%20Library/smbus2/i2cEncoderLibV2.py

import argparse
import random
import socket
import time
from itertools import cycle

import smbus2
from gpiozero import Button
import i2cEncoderLibV2
from pythonosc import udp_client
from pythonosc import osc_message_builder




MIN_VAL, MAX_VAL = 0, 20.0
DEVICES = [
    [0x71, 0x19, 0x23, 0x0d, 0x0f],
    [0x40, 0x9,  0x41, 0x5,  0x21],
    [0x11, 0x20, 0x3,  0x10, 0x4],
    [0x15, 0x8,  0x31, 0x7,  0x25],
    [0x47]
]
wrap_encoder             = [0x71, 0x40, 0x11, 0x15]
osc_address_patterns     = ["/switch", "/amp", "/rate", "/start", "/dur", "/pitch"]
osc_address_patterns_alt = ["/attach", "/pitch"]

def load_buttons():
    buttons_gpio = [13, 19, 26, 11, 5, 6, 9, 10, 17, 22, 27]

    return [Button(b_num) for b_num in buttons_gpio]

def init_encoder(device):
    bus = smbus2.SMBus(1)
    encoder = i2cEncoderLibV2.i2cEncoderLibV2(bus, device)

    encconfig = (i2cEncoderLibV2.INT_DATA |
                 i2cEncoderLibV2.DIRE_RIGHT |
                 i2cEncoderLibV2.IPUP_ENABLE |
                 i2cEncoderLibV2.RMOD_X1 |
                 i2cEncoderLibV2.RGB_ENCODER)
    if(device in wrap_encoder):
        encconfig = encconfig | i2cEncoderLibV2.WRAP_ENABLE

    encoder.begin(encconfig)
    encoder.writeCounter(MAX_VAL / 2)
    encoder.writeMax(MAX_VAL)
    encoder.writeMin(MIN_VAL)
    encoder.writeStep(1)
    encoder.writeInterruptConfig(0xff)

    return encoder

def send_msg(address, channel, value):
    msg = osc_message_builder.OscMessageBuilder(address=address)
    msg.add_arg(channel, arg_type = 'i')
    msg.add_arg(value, arg_type = 'i')
    msg = msg.build()
    client.send(msg)

def run_encoder(encoder, idx, stepIncrease, channel):
    EXP_GROWTH = 3
    counter    = encoder.readCounter32()
    value      = counter
    # Default colors values
    color      = '0x00'
    printColor = "Off"

    # Set color Red
    if counter > MAX_VAL / 2:
        color_step = (MAX_VAL - counter + 1) ** EXP_GROWTH
        color      = '0x{:02x}0000'.format(int(255 / color_step))
        printColor = "Red"

    # Set color Blue
    if counter < MAX_VAL / 2:
        colorStep  = counter + 1 ** EXP_GROWTH
        color      = '0x0000{:02x}'.format(int(255 / colorStep))
        printColor = "Blue"
    
    # Sample /switch
    if (idx == 0 and stepIncrease and channel != 4):
        value = stepIncrease

    if (not encoder.readStatus(i2cEncoderLibV2.RMAX) and
            not encoder.readStatus(i2cEncoderLibV2.RMIN)):
        encoder.writeRGBCode(int(color, 0))
        osc_address_pattern = osc_address_patterns[idx]
        if channel == 4:
            osc_address_pattern = osc_address_patterns[5]
            channel = -1
        send_msg(osc_address_pattern, channel, value)
        print('{} {} {} ({}, {})'.format(osc_address_pattern, channel, value, printColor, color))

def read_encoders(encoders):
    for channel, row in enumerate(encoders):
        for idx, encoder in enumerate(row):
            # Play: if play.is_pressed:
            encoder.updateStatus()

            # Encoder turns right
            if encoder.readStatus(i2cEncoderLibV2.RINC):
                run_encoder(encoder, idx, 1, channel)

            # Encoder turns left
            if encoder.readStatus(i2cEncoderLibV2.RDEC):
                run_encoder(encoder, idx, -1, channel)

            # Encoder is pushed
            if encoder.readStatus(i2cEncoderLibV2.PUSHP):
                if osc_address_patterns[idx] == "/amp":
                    print("/mute")
                else:
                    encoder.writeCounter(random.randint(MIN_VAL, MAX_VAL))
                    run_encoder(encoder, idx, False, channel)
            

def read_buttons(buttons, button_status):
    for i, button in enumerate(buttons):
        idx = i % len(buttons)
        if button.is_pressed:
            if button_status[idx] is False:
                print("button " + str(button.pin) + " pressed")
                button_status[idx] = True
        else:
            if button_status[idx] is True:
                print("button " + str(button.pin) + " not pressed")
                button_status[idx] = False




def load_encoders():
    encoders = []
    for idx, channel in enumerate(DEVICES):
        encoders.append([])
        for value in channel:
            encoders[idx].append(init_encoder(value))

    return encoders


if __name__ == "__main__":
    print('Running Samplematic on the {}'.format(socket.gethostname().capitalize()))
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default = "127.0.0.1",
                        help="The ip of the OSC server")
    parser.add_argument("--port", type = int, default = 57121,
                        help = "The port the OSC server is listening on")
    args = parser.parse_args()
    #client = udp_client.SimpleUDPClient(args.ip, args.port)
    client = udp_client.SimpleUDPClient("192.168.8.130", args.port)

    encoders = load_encoders()
    buttons = load_buttons()
    button_status = [False] * len(buttons)

    try:
        while True:
            read_buttons(buttons, button_status)
            read_encoders(encoders)
            time.sleep(0.1)
        
    except KeyboardInterrupt:
        for row in encoders:
            for encoder in row:
                encoder.writeRGBCode(0)
