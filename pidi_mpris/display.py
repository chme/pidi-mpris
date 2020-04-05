
from PIL import Image, ImageDraw, ImageFont
import ST7789 as ST7789


class Screen:
    def nextFrame(self):
        pass


class Display:

    def __init__(self, font):
        self.font = ImageFont.truetype(font, 20)

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

        self.txtImage = Image.new(
            'RGB', (self.width, self.height), color=(0, 0, 0))
        self.txtDraw = ImageDraw.Draw(self.txtImage)

    def imageFile(self, imageFile):
        image = Image.open(imageFile)

        # Resize the image
        image = image.resize((self.disp.width, self.disp.height))

        # Draw the image on the display hardware.
        print('Drawing image')

        self.disp.display(image)

    def text(self, text, align='center', valign='middle', spacing=4, font=None):
        self.txtDraw.rectangle((0, 0, self.width, self.height), (0, 0, 0))
        txtWidth, txtHeight = self.txtDraw.textsize(
            text, font, spacing=spacing)

        posX = self._posX(txtWidth, align, spacing)
        posY = self._posY(txtHeight, valign, spacing)
        self.txtDraw.text((posX, posY), text, font=font, fill=(
            255, 255, 255), align='center', spacing=spacing)
        self.disp.display(self.txtImage)

        pass

    def _posX(self, width, align, spacing):
        if align == 'left':
            return spacing
        elif align == 'right':
            return self.width - width - spacing
        else:
            return (self.width - width) // 2

    def _posY(self, height, valign, spacing):
        if valign == 'top':
            return spacing
        elif valign == 'bottom':
            return self.height - height - spacing
        else:
            return (self.height - height) // 2
