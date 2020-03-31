
from PIL import Image
import ST7789 as ST7789


class Display:

    def __init__(self):
        self.disp = ST7789.ST7789(
            port=0,
            cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
            dc=9,
            # 18 for back BG slot, 19 for front BG slot.
            backlight=13,
            spi_speed_hz=80 * 1000 * 1000)

        # Initialize display.
        self.disp.begin()

    def set(self, imageFile):
        image = Image.open(imageFile)

        # Resize the image
        image = image.resize((self.disp.width, self.disp.height))

        # Draw the image on the display hardware.
        print('Drawing image')

        self.disp.display(image)
