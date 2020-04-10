

def color_hex_to_rgb(color):
    h = color.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
