

from .buttons import Button
from .display import Display
from .mpris import MPRIS


class Screen:

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        pass

    def onButtonPressed(self, button: Button) -> None:
        pass

    def onPlayerUpdate(self) -> None:
        pass


class ArtworkScreen(Screen):
    def __init__(self, conf: dict, display: Display, mprisPlayer: MPRIS) -> None:
        self._defaultImage = conf['DEFAULTS']['default_image']
        self._display = display
        self._mprisPlayer = mprisPlayer
        self._artUrl = None

    def activate(self) -> None:
        self._showArtwork()

    def deactivate(self) -> None:
        self._artUrl = None

    def onButtonPressed(self, button: Button) -> None:
        if button == Button.A:
            self._mprisPlayer.previous()
        elif button == Button.X:
            self._mprisPlayer.next()
        elif button == Button.Y:
            self._mprisPlayer.playPause()

    def onPlayerUpdate(self) -> None:
        self._showArtwork()

    def _showArtwork(self):
        artUrl = self._mprisPlayer.artUrl()

        if artUrl.startswith('file://'):
            artUrl = artUrl[len('file://'):]
        else:
            artUrl = self._defaultImage

        if self._artUrl is None or self._artUrl != artUrl:
            self._artUrl = artUrl
            self._display.imageFile(artUrl)
