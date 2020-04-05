
from PIL import ImageFont

from .buttons import Button
from .display import Display, TextImage
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


class NowPlayingInfoScreen(Screen):
    def __init__(self, conf: dict, display: Display, mprisPlayer: MPRIS) -> None:
        self._display = display
        self._mprisPlayer = mprisPlayer
        self._conf = conf

        self._fonts = []
        self._fonts.append(ImageFont.truetype(conf['NowPlayingInfoScreen']['line1_font'], int(
            conf['NowPlayingInfoScreen']['line1_font_size'])))
        self._fonts.append(ImageFont.truetype(conf['NowPlayingInfoScreen']['line2_font'], int(
            conf['NowPlayingInfoScreen']['line2_font_size'])))
        self._fonts.append(ImageFont.truetype(conf['NowPlayingInfoScreen']['line3_font'], int(
            conf['NowPlayingInfoScreen']['line3_font_size'])))
        self._fonts.append(ImageFont.truetype(conf['NowPlayingInfoScreen']['line4_font'], int(
            conf['NowPlayingInfoScreen']['line4_font_size'])))

        self._texts = []
        self._texts.append(conf['NowPlayingInfoScreen']['line1_text'])
        self._texts.append(conf['NowPlayingInfoScreen']['line2_text'])
        self._texts.append(conf['NowPlayingInfoScreen']['line3_text'])
        self._texts.append(conf['NowPlayingInfoScreen']['line4_text'])

        print(self._texts)

        self._txtImage = TextImage(self._display.width, self._display.height)

    def activate(self) -> None:
        self._showInfo()

    def deactivate(self) -> None:
        pass

    def onButtonPressed(self, button: Button) -> None:
        if button == Button.A:
            self._mprisPlayer.previous()
        elif button == Button.X:
            self._mprisPlayer.next()
        elif button == Button.Y:
            self._mprisPlayer.playPause()

    def onPlayerUpdate(self) -> None:
        self._showInfo()

    def _showInfo(self):
        self._txtImage.reset()

        artist = ', '.join(self._mprisPlayer.artist())
        album = self._mprisPlayer.album()
        title = self._mprisPlayer.title()
        for i, t in enumerate(self._texts):
            if len(t) > 0:
                print(t)
                print('template: {}'.format(t))
                print(t.format(artist=artist, album=album, title=title))
                self._txtImage.add(
                    t.format(artist=artist, album=album, title=title), self._fonts[i])

        self._display.image(self._txtImage.draw())


class ArtworkScreen(Screen):
    def __init__(self, conf: dict, display: Display, mprisPlayer: MPRIS) -> None:
        self._defaultImage = conf['DEFAULT']['default_image']
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
