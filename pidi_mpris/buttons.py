'''
The MIT License (MIT)

Copyright (c) 2020 Christian Meffert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from enum import Enum
import logging
from time import sleep, time

import RPi.GPIO as GPIO


log = logging.getLogger(__name__)


class Button(Enum):
    # The buttons on Pirate Audio are connected to pins 5, 6, 16 and 20
    A = (5, 'A')
    B = (6, 'B')
    X = (16, 'X')
    Y = (20, 'Y')

    def __new__(cls, pin,  label):
        obj = object.__new__(cls)
        obj._value_ = pin
        obj.label = label
        return obj


class Buttons:

    def __init__(self):
        self.buttonHandler = None
        self.bouncetime = 300
        self.bouncetimeInSeconds = self.bouncetime / 1000
        self.lastEventTime = 0

        # Set up RPi.GPIO with the "BCM" numbering scheme
        GPIO.setmode(GPIO.BCM)

        # Buttons connect to ground when pressed, so we should set them up
        # with a "PULL UP", which weakly pulls the input signal to 3.3V.
        for button in Button:
            GPIO.setup(button.value, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(
                button.value, GPIO.FALLING, self.onButtonPressed, bouncetime=self.bouncetime)

    def cleanup(self):
        for button in Button:
            GPIO.cleanup(button.value)

    def onPressedHandler(self, cb):
        self.onPressed = cb

    def onLongPressHandler(self, cb):
        self.onLongPress = cb

    def onReleasedHandler(self, cb):
        self.onReleased = cb

    def onButtonPressed(self, pin):
        if time() - self.lastEventTime < self.bouncetimeInSeconds:
            log.debug('Ignoring button press on %s (bouncetime)', pin)
            return

        button = Button(pin)
        log.debug('Button pressed %s', button)

        self.lastEventTime = time()

        if self.onPressed:
            if not self.onPressed(button):
                return

        i = 0
        secondsPressed = 0
        while GPIO.input(pin) == GPIO.LOW:
            self.lastEventTime = time()
            sleep(0.1)
            i = i + 1

            if i % 10 == 0:
                secondsPressed = secondsPressed + 1
                log.debug('Button %ss pressed (iteration=%s)',
                          secondsPressed, i)

                if self.onLongPress:
                    log.debug('Long button pressed %s (%s s)',
                              button, secondsPressed)
                    if not self.onLongPress(button, secondsPressed):
                        return

        self.lastEventTime = time()

        log.debug('Button released %s (%s s)', button, secondsPressed)
        if self.onReleased:
            self.onReleased(button, secondsPressed)
