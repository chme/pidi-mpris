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

import csv
import logging
from PIL import Image, ImageFont
import threading

from .buttons import Button
from .display import TextImage
from .util import color_hex_to_rgb


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
        self._conf = conf['GifScreen']

        parser = csv.reader([self._conf['image']])
        self._images = [item for sublist in parser for item in sublist]

        self._activeImage = 0
        self._numImages = len(self._images)

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

    def onButtonPressed(self, button):
        if button == Button.Y:
            if self._numImages > 1:
                self.deactivate()
                self._activeImage = (self._activeImage + 1) % self._numImages
                self.activate()

    def _showGif(self):
        image = Image.open(self._images[self._activeImage])

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
        self._conf = conf['NowPlayingInfoScreen']

        self._fonts = []
        self._fonts.append(ImageFont.truetype(
            self._conf['line1_font_face'], int(self._conf['line1_font_size'])))
        self._fonts.append(ImageFont.truetype(
            self._conf['line2_font_face'], int(self._conf['line2_font_size'])))
        self._fonts.append(ImageFont.truetype(
            self._conf['line3_font_face'], int(self._conf['line3_font_size'])))
        self._fonts.append(ImageFont.truetype(
            self._conf['line4_font_face'], int(self._conf['line4_font_size'])))

        self._bgColor = color_hex_to_rgb(self._conf['background'])

        self._colors = []
        self._colors.append(color_hex_to_rgb(self._conf['line1_font_color']))
        self._colors.append(color_hex_to_rgb(self._conf['line2_font_color']))
        self._colors.append(color_hex_to_rgb(self._conf['line3_font_color']))
        self._colors.append(color_hex_to_rgb(self._conf['line4_font_color']))

        log.debug('Text colors: %s', self._colors)

        self._texts = []
        self._texts.append(self._conf['line1_text'])
        self._texts.append(self._conf['line2_text'])
        self._texts.append(self._conf['line3_text'])
        self._texts.append(self._conf['line4_text'])

        log.debug('Text templates: %s', self._texts)

        self._txtImage = TextImage(
            self._display.width, self._display.height, bgColor=self._bgColor)

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
                    t.format(artist=artist, album=album, title=title), self._fonts[i], color=self._colors[i])

        self._display.image(self._txtImage.draw())


class ArtworkScreen(Screen):
    def __init__(self, conf, display, mprisPlayer):
        self._conf = conf['ArtworkScreen']
        self._defaultImage = self._conf['fallback_image']
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
