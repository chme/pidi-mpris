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
DEFAULT_FONT_PATH = '/usr/share/pidi-mpris/fonts/OpenSans/OpenSans-Regular.ttf'


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
            'default_font': DEFAULT_FONT_PATH,
            'default_font_size': 30},
        'NowPlayingInfoScreen': {
            'line1_text': '%artist%',
            'line1_font': '${default_font}',
            'line1_font_size': '${default_font_size}',
            'line2_text': '%title%',
            'line2_font': '${default_font}',
            'line2_font_size': '${default_font_size}',
            'line3_text': '%album%',
            'line3_font': '${default_font}',
            'line3_font_size': '${default_font_size}',
            'line4_text': '',
            'line4_font': '${default_font}',
            'line4_font_size': '${default_font_size}}'},
        'GENERAL': {
            'log_level': 'WARNING',
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

    log.info('Init complete, press Ctrl+C to exit')

    signal.signal(signal.SIGINT, end)

    try:
        loop = GLib.MainLoop()
        loop.run()
    finally:
        player.deinit()


if __name__ == '__main__':
    main()
