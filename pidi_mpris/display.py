
import logging
import textwrap

from PIL import Image, ImageDraw
import ST7789 as ST7789


log = logging.getLogger(__name__)


class Text:
    def __init__(self, text, font, imageDraw, maxWidth=None, align='center', lineSpacing=4, margin=(4, 4), color=(255, 255, 255)):
        self.text = text
        self.font = font
        self.draw = imageDraw
        self.align = align
        self.lineSpacing = lineSpacing
        self.margin = margin
        self.color = color

        self.width, self.height = self._calcSize(maxWidth)

    def _calcSize(self, maxWidth):
        if len(self.text) == 0:
            return 0, 0

        width, height = self.draw.textsize(
            self.text, self.font, spacing=self.lineSpacing)

        if maxWidth and maxWidth < width:
            avgLetterWidth = width / len(self.text)
            maxLetter = maxWidth // avgLetterWidth

            wrapper = textwrap.TextWrapper(width=maxLetter)
            self.text = wrapper.fill(self.text)

            log.debug('Wrapped text "%s" (original size=%sx%s, avg letter width=%s, max letters=%s)',
                      self.text, width, height, avgLetterWidth, maxLetter)
            width, height = self.draw.textsize(
                self.text, self.font, spacing=self.lineSpacing)

        height = height + self.margin[0] + self.margin[1]
        log.debug('Text size: %sx%s (margin=%s)', width, height, self.margin)
        return width, height

    def drawText(self, x, y, width):
        if len(self.text) == 0:
            return

        posX = x + self._posX(width)
        posY = y + self.margin[0]
        self.draw.text((posX, posY), self.text, font=self.font,
                       fill=self.color, align=self.align, spacing=self.lineSpacing)

    def _posX(self, width):
        if self.align == 'left':
            return 0
        elif self.align == 'right':
            return width - self.width
        else:
            return (width - self.width) // 2


class TextImage:
    def __init__(self, width, height, color=(255, 255, 255), bgColor=(0, 0, 0), valign='middle', margin=4):
        self._width = width
        self._height = height
        self._color = color
        self._bgColor = bgColor
        self._valign = valign
        self._margin = margin

        self._texts = []
        self._innerWidth = self._width - (2 * self._margin)
        self._innerHeight = self._height - (2 * self._margin)

        self._image = Image.new(
            'RGB', (self._width, self._height), color=self._bgColor)
        self._draw = ImageDraw.Draw(self._image)

    def add(self, text, font):
        self._texts.append(Text(text, font, self._draw,
                                maxWidth=self._innerWidth, color=self._color))

    def reset(self):
        self._texts = []

    def draw(self):
        self._draw.rectangle((0, 0, self._width, self._height), self._bgColor)

        posX = self._margin

        txtHeight = sum(list(map(lambda a: a.height, self._texts)))
        posY = self._posY(self._innerHeight, txtHeight,
                          self._valign) + self._margin

        for txt in self._texts:
            txt.drawText(posX, posY, self._innerWidth)
            posY += txt.height
        return self._image

    def _posY(self, height, txtHeight, valign):
        if valign == 'top':
            return 0
        elif valign == 'bottom':
            return height - txtHeight
        else:
            return (height - txtHeight) // 2


class Display:

    def __init__(self):
        self.disp = ST7789.ST7789(
            port=0,
            cs=ST7789.BG_SPI_CS_FRONT,
            dc=9,
            backlight=13,  # 13 for Pirate Audio
            spi_speed_hz=80 * 1000 * 1000)

        # Initialize display.
        self.disp.begin()

        self.width = self.disp.width
        self.height = self.disp.height

    def image(self, image):
        self.disp.display(image)

    def imageFile(self, imageFile):
        image = Image.open(imageFile)

        # Resize the image
        image = image.resize((self.disp.width, self.disp.height))

        # Draw the image on the display hardware.
        log.debug('Drawing image %s', imageFile)

        self.disp.display(image)
