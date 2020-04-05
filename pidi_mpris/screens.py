
from .buttons import Button


class ArtworkScreen:
    def __init__(self, conf, display, mprisPlayer):
        self._defaultImage = conf.get('default_image')

        self._display = display
        self._mprisPlayer = mprisPlayer
        self._artUrl = None

    def activate(self):
        self._showArtwork()

    def deactivate(self):
        pass

    def onButtonPressed(self, button):

        if button == Button.A:
            self._mprisPlayer.previous()
        elif button == Button.X:
            self._mprisPlayer.next()
        elif button == Button.Y:
            self._mprisPlayer.playPause()

    def onPlayerUpdate(self):
        self._showArtwork()

    def _showArtwork(self):
        artUrl = self.mprisPlayer.artUrl()

        if artUrl.startswith('file://'):
            artUrl = artUrl[len('file://'):]
        else:
            artUrl = self._defaultImage

        if self._artUrl is None or self._artUrl != artUrl:
            self._artUrl = artUrl
            self._display.imageFile(artUrl)
