
import logging

from .buttons import Buttons, Button
from .display import Display
from .mpris import MPRIS
from .screens import ArtworkScreen, NowPlayingInfoScreen, GifScreen


log = logging.getLogger(__name__)


class Player:
    def __init__(self, busName, conf):
        self._busName = busName
        self._conf = conf

    def init(self):
        self._mprisPlayer = MPRIS(self._busName)
        self._mprisPlayer.setUpdateHandler(self._onPlayerUpdate)

        log.debug('Initializing display')

        self._display = Display()

        log.debug('Initializing buttons: %s', list(Button))

        self._buttons = Buttons()
        self._buttons.onPressedHandler(self._onButtonPressed)
        self._buttons.onLongPressHandler(self._onButtonLongPress)
        self._buttons.onReleasedHandler(self._onButtonReleased)

        self._screens = [
            ArtworkScreen(self._conf, self._display, self._mprisPlayer),
            NowPlayingInfoScreen(self._conf, self._display, self._mprisPlayer),
            GifScreen(self._conf, self._display)
        ]
        self._activeScreenIndex = 0
        self._activeScreen = self._screens[self._activeScreenIndex]
        self._activeScreen.activate()

    def deinit(self):
        self._buttons.cleanup()

    def _onPlayerUpdate(self):
        log.info('Player update: %s [%s/%s/%s, artwork=%s]',
                 self._mprisPlayer.playbackStatus(),
                 ','.join(self._mprisPlayer.artist()),
                 self._mprisPlayer.album(),
                 self._mprisPlayer.title(),
                 self._mprisPlayer.artUrl())

        self._activeScreen.onPlayerUpdate()

    def _onButtonPressed(self, button):
        log.debug('Button press detected: %s', button)

        if button == Button.B:
            pass
        else:
            self._activeScreen.onButtonPressed(button)

    def _onButtonLongPress(self, button, secondsPressed):
        if button == Button.B:
            if secondsPressed == 3:
                log.debug('Long press: %s', self._activeScreenIndex)
                self._display.setBacklight(not self._display.status())
        else:
            self._activeScreen.onButtonLongPress(button, secondsPressed)

    def _onButtonReleased(self, button, secondsPressed):
        if button == Button.B:
            if secondsPressed < 3 and self._display.status():
                self._switchToNextScreen()
        else:
            self._activeScreen._onButtonReleased(button, secondsPressed)

    def _switchToNextScreen(self):
        if len(self._screens) > 1:
            self._activeScreen.deactivate()
            self._activeScreenIndex = (
                self._activeScreenIndex + 1) % len(self._screens)

            log.debug('Activate next screen: %s', self._activeScreenIndex)

            self._activeScreen = self._screens[self._activeScreenIndex]
            self._activeScreen.activate()
