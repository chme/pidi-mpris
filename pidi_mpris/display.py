
from functools import reduce

from PIL import Image, ImageDraw
import ST7789 as ST7789


class Text:
    def __init__(self, text: str, font, spacing: int = 4) -> None:
        self.text = text
        self.font = font
        self.spacing = spacing

    def size(self, draw: ImageDraw) -> tuple:
        return draw.textsize(self.text, self.font, spacing=self.spacing)


class TextImage:
    def __init__(self, width: int, height: int, align: str = 'center', valign='middle', margin: int = 4, color: tuple = (255, 255, 255), bgColor: tuple = (0, 0, 0)) -> None:
        self._width = width
        self._height = height
        self._align = align
        self._valign = valign
        self._margin = margin
        self._color = color
        self._bgColor = bgColor

        self._texts = []

        self._image = Image.new(
            'RGB', (self._width, self._height), color=self._bgColor)
        self._draw = ImageDraw.Draw(self._image)

    def add(self, text: str, font, spacing: int = 4) -> None:
        self._texts.append(Text(text, font, spacing=spacing))

    def reset(self):
        self._texts = []

    def draw(self):
        self._draw.rectangle((0, 0, self._width, self._height), self._bgColor)

        sizes = [t.size(self._draw) for t in self._texts]
        txtWidth, txtHeight = reduce(
            lambda a, b: (max(a[0], b[0]), a[1] + b[1]), sizes)

        innerWidth = self._width - (2 * self._margin)
        posX = self._posX(innerWidth, txtWidth, self._align) + self._margin
        innerHeight = self._height - (2 * self._margin)
        posY = self._posY(innerHeight, txtHeight, self._valign) + self._margin

        x = posX
        y = posY
        for i, t in enumerate(self._texts):
            x = self._posX(innerWidth, sizes[i][0], self._align) + self._margin
            self._draw.text((x, y), t.text, font=t.font,
                            fill=self._color, align=self._align, spacing=t.spacing)
            y += sizes[i][1]

        return self._image

    def _posX(self, width, elemWidth, align):
        if align == 'left':
            return 0
        elif align == 'right':
            return width - elemWidth
        else:
            return (width - elemWidth) // 2

    def _posY(self, height, elemHeight, valign):
        if valign == 'top':
            return 0
        elif valign == 'bottom':
            return height - elemHeight
        else:
            return (height - elemHeight) // 2


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
        print('Drawing image')

        self.disp.display(image)
