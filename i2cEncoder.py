# I2CEncoderV2
# Library: https://github.com/Fattoresaimon/I2CEncoderV2/blob/master/Raspberry%20Library/smbus2/i2cEncoderLibV2.py
# Date: 2019/05/17
# Author: https://github.com/retroriff

import smbus2
from gpiozero import Button 
from time import sleep
import i2cEncoderLibV2
import random

bus = smbus2.SMBus(1)
int_pin = Button(4)

encoder = i2cEncoderLibV2.i2cEncoderLibV2(bus,0x21)

encconfig = (i2cEncoderLibV2.INT_DATA | i2cEncoderLibV2.WRAP_DISABLE | i2cEncoderLibV2.DIRE_RIGHT | i2cEncoderLibV2.IPUP_ENABLE | i2cEncoderLibV2.RMOD_X1 | i2cEncoderLibV2.RGB_ENCODER)
encoder.begin(encconfig)

maxValue = 10.0
minValue = 0
expGrowth=3

encoder.writeCounter(maxValue/2)
encoder.writeMax(maxValue)
encoder.writeMin(minValue)
encoder.writeStep(1)
encoder.writeInterruptConfig(0xff)

try:
  while True:
    if int_pin.is_pressed :
      encoder.updateStatus()
      changeColor=0

      # Encoder turn right
      if encoder.readStatus(i2cEncoderLibV2.RINC) == True :
        changeColor=1

      # Encoder turn left
      if encoder.readStatus(i2cEncoderLibV2.RDEC) == True :
        changeColor=1

      # Encoder pushed
      if encoder.readStatus(i2cEncoderLibV2.PUSHP) == True :
        print("Click")
        encoder.writeCounter(random.randint(minValue,maxValue))
        changeColor=1

      if changeColor==1 :
        # Set color Red
        if encoder.readCounter32() > maxValue/2 :
            colorStep = int((maxValue - encoder.readCounter32()+1)**expGrowth)
            c = int(255 / colorStep)
            color = '0x{:02x}{:02x}{:02x}'.format( c, 0 , 0 )
            printColor = "Red"

        # Set no color
        if encoder.readCounter32() == maxValue/2 :
            c = 0
            color = '0x00'
            printColor = "Off"

        # Set color Blue
        if encoder.readCounter32() < maxValue/2 :
            colorStep = int((encoder.readCounter32()+1)**expGrowth)
            c = int(255 / colorStep)
            color = '0x{:02x}{:02x}{:02x}'.format( 0, 0 , c )
            printColor = "Blue"

        if encoder.readStatus(i2cEncoderLibV2.RMAX) != True and encoder.readStatus(i2cEncoderLibV2.RMIN) != True :
          encoder.writeRGBCode(int(color, 0))
          print ('Counter: %d %s: %d' % (encoder.readCounter32(),  printColor, c))

except KeyboardInterrupt:
  encoder.writeInterruptConfig(0xff)
  print("\nExit.")