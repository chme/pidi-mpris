#!/usr/bin/python3

import argparse
import configparser
import logging
import signal

from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop

from .player import Player


DEFAULT_CONF_FILE_PATH = '/etc/pidi-mpris.conf'

DEFAULT_IMAGE_PATH = '/usr/share/pidi-mpris/images/luana-de-marco-PF1l1F1hzoU-unsplash.png'
DEFAULT_GIF_PATH = '/usr/share/pidi-mpris/images/deployrainbows.gif'

FONT_FACE_REGULAR = '/usr/share/pidi-mpris/fonts/OpenSans/OpenSans-Regular.ttf'
FONT_FACE_BOLD = '/usr/share/pidi-mpris/fonts/OpenSans/OpenSans-Bold.ttf'
FONT_FACE_ITALIC = '/usr/share/pidi-mpris/fonts/OpenSans/OpenSans-Italic.ttf'

FONT_SIZE_SMALL = 20
FONT_SIZE_NORMAL = 25
FONT_SIZE_LARGE = 30

FONT_COLOR_DEFAULT = '#FFFFFF'
FONT_COLOR_PRIMARY = '#EBFFFC'
FONT_COLOR_MUTED = '#F5F5F5'

BACKGROUND_COLOR = '#000000'


def end(_signal, _frame):
    global loop
    print('Ctrl+C captured, exiting program.')
    loop.quit()


def parse_arguments():
    parser = argparse.ArgumentParser(description='Pirate Audio MPRIS')
    parser.add_argument('-m',
                        '--mpris',
                        help='DBus name of the MPRIS media player (has to start with "org.mpris.MediaPlayer2.")')
    parser.add_argument('-c',
                        '--conf',
                        default=DEFAULT_CONF_FILE_PATH,
                        help='Path to configuration file')
    parser.add_argument('-l',
                        '--log-level',
                        help='Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('-f',
                        '--log-filename',
                        help='Log file (omit to log to std.err)')

    return parser.parse_args()


def read_conf(args):
    confFile = args.conf
    conf = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation())

    conf.read_dict({
        'DEFAULT': {
            'default_image': DEFAULT_IMAGE_PATH,
            'default_gif': DEFAULT_GIF_PATH,
            'font_face_regular': FONT_FACE_REGULAR,
            'font_face_bold': FONT_FACE_BOLD,
            'font_face_italic': FONT_FACE_ITALIC,
            'font_size_small': FONT_SIZE_SMALL,
            'font_size_normal': FONT_SIZE_NORMAL,
            'font_size_large': FONT_SIZE_LARGE,
            'font_color_default': FONT_COLOR_DEFAULT,
            'font_color_primary': FONT_COLOR_PRIMARY,
            'font_color_muted': FONT_COLOR_MUTED,
            'background_color': BACKGROUND_COLOR},
        'NowPlayingInfoScreen': {
            'background': '${background_color}',
            'line1_text': '{artist}',
            'line1_font_face': '${font_face_regular}',
            'line1_font_size': '${font_size_normal}',
            'line1_font_color': '${font_color_default}',
            'line2_text': '{title}',
            'line2_font_face': '${font_face_bold}',
            'line2_font_size': '${font_size_normal}',
            'line2_font_color': '${font_color_primary}',
            'line3_text': '{album}',
            'line3_font_face': '${font_face_regular}',
            'line3_font_size': '${font_size_small}',
            'line3_font_color': '${font_color_muted}',
            'line4_text': '',
            'line4_font_face': '${font_face_regular}',
            'line4_font_size': '${font_size_small}',
            'line4_font_color': '${font_color_muted}'},
        'GENERAL': {
            'log_level': 'INFO',
            'log_filename': ''}
    })
    conf.read(confFile)

    if args.log_level:
        conf['GENERAL']['log_level'] = args.log_level
    if args.log_filename:
        conf['GENERAL']['log_filename'] = args.log_filename

    return conf


def log_config(conf):
    level = getattr(logging, conf['GENERAL']['log_level'].upper(), None)
    if not isinstance(level, int):
        raise ValueError('Invalid log level: {}'.format(level))

    logging.basicConfig(level=level, filename=conf['GENERAL']['log_filename'],
                        format='%(asctime)s %(levelname)8s [%(name)8s] %(message)s')

    return logging.getLogger(__name__)


def main():
    global mpris_player, display, buttons, loop, conf

    DBusGMainLoop(set_as_default=True)

    args = parse_arguments()
    conf = read_conf(args)

    log = log_config(conf)

    log.debug('Configuration file: %s', args.conf)
    log.debug('Configuration: %s', {section: dict(
        conf[section]) for section in conf.sections()})

    log.debug('Initializing MPRIS player %s', args.mpris)

    player = Player(args.mpris, conf)
    player.init()

    print('Init complete, press Ctrl+C to exit')

    signal.signal(signal.SIGINT, end)

    try:
        loop = GLib.MainLoop()
        loop.run()
    finally:
        player.deinit()


if __name__ == '__main__':
    main()
