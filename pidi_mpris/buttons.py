
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

    def _onButtonPressed(self, pin):
        if self.buttonHandler:
            self.buttonHandler(Button(pin))

    def onButtonPressed(self, pin):
        if time() - self.lastEventTime < self.bouncetime:
            log.debug('Ignoring button press on %s (bouncetime)', pin)
            return

        button = Button(pin)
        log.debug('Button pressed %s', button)

        if self.onPressed:
            self.onPressed(button)

        self.lastButtonPressedTime = time()

        i = 0
        secondsPressed = 0
        while GPIO.input(self.pin) == GPIO.LOW:
            self.lastEventTime = time()
            sleep(0.1)
            i = i + 1

            if i % 10 == 0:
                secondsPressed = secondsPressed + 1

                if self.onLongPress:
                    log.debug('Long button pressed %s (%s s)',
                              button, secondsPressed)
                    self.onLongPress(button, secondsPressed)

        self.lastEventTime = time()

        if self.onReleased:
            log.debug('Button released %s (%s s)', button, secondsPressed)
            self.onReleased(button, secondsPressed)
