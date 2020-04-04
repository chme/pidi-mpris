
from enum import Enum
import RPi.GPIO as GPIO


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

        # Set up RPi.GPIO with the "BCM" numbering scheme
        GPIO.setmode(GPIO.BCM)

        # Buttons connect to ground when pressed, so we should set them up
        # with a "PULL UP", which weakly pulls the input signal to 3.3V.
        for button in Button:
            GPIO.setup(button.value, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(
                button.value, GPIO.FALLING, self.onButtonPressed, bouncetime=300)

    def cleanup(self):
        for button in Button:
            GPIO.cleanup(button.value)

    def setButtonHandler(self, cb):
        self.buttonHandler = cb

    def onButtonPressed(self, pin):
        if self.buttonHandler:
            self.buttonHandler(Button(pin))
