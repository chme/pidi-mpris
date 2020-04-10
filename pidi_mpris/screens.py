
import logging
from PIL import Image, ImageFont
import threading

from .buttons import Button
from .display import TextImage


log = logging.getLogger(__name__)


class Screen:

    def activate(self):
        pass

    def deactivate(self):
        pass

    def onButtonPressed(self, button):
        pass

    def onButtonLongPress(self, button, secondsPressed):
        pass

    def onButtonReleased(self, button, secondsPressed):
        pass

    def onPlayerUpdate(self):
        pass


class GifScreen(Screen):
    def __init__(self, conf, display):
        self._display = display
        self._conf = conf

        self._defaultImage = conf['DEFAULT']['default_gif']
        self._irq = threading.Event()
        self._thread = threading.Thread(name='gif', target=self._showGif)

    def activate(self):
        self._irq.clear()
        self._thread = threading.Thread(name='gif', target=self._showGif)
        self._thread.start()

    def deactivate(self):
        self._irq.set()
        self._thread.join()
        self._thread = None

    def _showGif(self):
        image = Image.open(self._defaultImage)

        run = True
        frame = 0
        while run:
            try:
                image.seek(frame)
                self._display.image(image)
                frame += 1
                duration = 0.05
                if 'duration' in image.info:
                    duration = image.info['duration'] / 1000
                run = not self._irq.wait(duration)
            except EOFError:
                frame = 0


class NowPlayingInfoScreen(Screen):
    def __init__(self, conf, display, mprisPlayer):
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

        log.debug(self._texts)

        self._txtImage = TextImage(self._display.width, self._display.height)

    def activate(self):
        self._showInfo()

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
        self._showInfo()

    def _showInfo(self):
        self._txtImage.reset()

        artist = ', '.join(self._mprisPlayer.artist())
        album = self._mprisPlayer.album()
        title = self._mprisPlayer.title()
        for i, t in enumerate(self._texts):
            if len(t) > 0:
                log.debug(t.format(artist=artist, album=album, title=title))
                self._txtImage.add(
                    t.format(artist=artist, album=album, title=title), self._fonts[i])

        self._display.image(self._txtImage.draw())


class ArtworkScreen(Screen):
    def __init__(self, conf, display, mprisPlayer):
        self._defaultImage = conf['DEFAULT']['default_image']
        self._display = display
        self._mprisPlayer = mprisPlayer
        self._artUrl = None

    def activate(self):
        self._showArtwork()

    def deactivate(self):
        self._artUrl = None

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
        artUrl = self._mprisPlayer.artUrl()

        if artUrl.startswith('file://'):
            artUrl = artUrl[len('file://'):]
        else:
            artUrl = self._defaultImage

        if self._artUrl is None or self._artUrl != artUrl:
            self._artUrl = artUrl
            self._display.imageFile(artUrl)
