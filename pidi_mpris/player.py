#!/usr/bin/python3

import argparse
import configparser
import signal
import sys

from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop

from .buttons import Buttons, Button
from .display import Display
from .mpris import MPRIS
from .screens import ArtworkScreen, NowPlayingInfoScreen


DEFAULT_CONF_FILE_PATH = '/etc/pidi-mpris.conf'

DEFAULT_IMAGE_PATH = '/usr/share/pidi-mpris/images/luana-de-marco-PF1l1F1hzoU-unsplash.png'
DEFAULT_FONT_PATH = '/usr/share/pidi-mpris/fonts/OpenSans/OpenSans-Regular.ttf'


class Player:
    def __init__(self, busName, conf):
        self._busName = busName
        self._conf = conf

    def init(self):
        self._mprisPlayer = MPRIS(self._busName)
        self._mprisPlayer.setUpdateHandler(self._onPlayerUpdate)

        print('Initializing display')

        self._display = Display()

        print('Initializing buttons: {}'.format(list(Button)))

        self._buttons = Buttons()
        self._buttons.setButtonHandler(self._onButtonPressed)

        self._screens = [
            ArtworkScreen(self._conf, self._display, self._mprisPlayer),
            NowPlayingInfoScreen(self._conf, self._display, self._mprisPlayer)]
        self._activeScreenIndex = 0
        self._activeScreen = self._screens[self._activeScreenIndex]
        self._activeScreen.activate()

    def deinit(self):
        self._buttons.cleanup()

    def _onPlayerUpdate(self):
        print('Player update: {}/{}/{}, artwork={}'.format(','.join(self._mprisPlayer.artist()),
                                                           self._mprisPlayer.album(),
                                                           self._mprisPlayer.title(),
                                                           self._mprisPlayer.artUrl()))

        self._activeScreen.onPlayerUpdate()

    def _onButtonPressed(self, button):
        print('Button press detected: {}'.format(button))

        if button == Button.B:
            if len(self._screens) > 1:
                self._activeScreen.deactivate()
                self._activeScreenIndex = (
                    self._activeScreenIndex + 1) % len(self._screens)

                print('Activate next screen: {}'.format(
                    self._activeScreenIndex))

                self._activeScreen = self._screens[self._activeScreenIndex]
                self._activeScreen.activate()
        else:
            self._activeScreen.onButtonPressed(button)


def end(_signal, _frame):
    global loop
    print('Ctrl+C captured, exiting program.')
    loop.quit()


def parse_arguments():
    parser = argparse.ArgumentParser(description='Pirate Audio MPRIS')
    parser.add_argument('-n',
                        '--name',
                        default=None,
                        help='DBus name of the media player (has to start with "org.mpris.MediaPlayer2.")')
    parser.add_argument('-c',
                        '--conf',
                        default=DEFAULT_CONF_FILE_PATH,
                        help='Path to configuration file')

    return parser.parse_args()


def read_conf(conf_file):
    print('Configuration file: {}'.format(conf_file))

    conf = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation())
    conf.read_dict({
        'DEFAULT': {
            'default_image': DEFAULT_IMAGE_PATH,
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
            'line4_font_size': '${default_font_size}}'}
    })
    conf.read(conf_file)
    return conf


def main():
    global mpris_player, display, buttons, loop, conf

    DBusGMainLoop(set_as_default=True)

    args = parse_arguments()
    conf = read_conf(args.conf)

    print('Configuration: {}'.format(
        {section: dict(conf[section]) for section in conf.sections()}))

    print('Initializing MPRIS player {}'.format(args.name))

    player = Player(args.name, conf)
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
