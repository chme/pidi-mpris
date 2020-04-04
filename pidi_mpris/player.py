#!/usr/bin/python3

import argparse
import signal
import sys

from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop

from .mpris import find_available_players, MPRIS
from .display import Display
from .buttons import Buttons, Button


def end(_signal, _frame):
    global loop
    print('Ctrl+C captured, exiting program.')
    loop.quit()


def on_player_update():
    global display, mpris_player

    print("Player update: {} - {} - {}, artwork={}".format(mpris_player.artist(),
                                                           mpris_player.album(),
                                                           mpris_player.title(),
                                                           mpris_player.artUrl()))

    artUrl = mpris_player.artUrl()
    if artUrl.startswith('file://'):
        display.set(artUrl[len('file://'):])


def on_button_pressed(button):
    global mpris_player

    print("Button press detected: {}".format(button))

    if button == Button.A:
        # Top-left button
        mpris_player.previous()
    elif button == Button.B:
        # Bottom-left button
        pass
    elif button == Button.X:
        # Top-right button
        mpris_player.next()
    elif button == Button.Y:
        # Bottom-right button
        mpris_player.playPause()


def parse_arguments():
    parser = argparse.ArgumentParser(description="Pirate Audio MPRIS")
    parser.add_argument('-n', '--name', default=None,
                        help="Bus name of the media player (has to start with 'org.mpris.MediaPlayer2.')")

    return parser.parse_args()


def find_mpris_bus_name(arg_bus_name):
    mpris_players = find_available_players()

    print("Available MPRIS players: {}".format(mpris_players))

    if arg_bus_name is None:
        if len(mpris_players) > 0:
            return mpris_players[0]
        return None

    if arg_bus_name in mpris_players:
        return arg_bus_name
    return None


def main():
    global mpris_player, display, buttons, loop

    DBusGMainLoop(set_as_default=True)

    args = parse_arguments()

    bus_name = find_mpris_bus_name(args.name)
    if bus_name is None:
        print("Unable to find MPRIS player '{}'".format(args.name))
        sys.exit(1)

    print("Connecting to MPRIS player '{}'".format(bus_name))

    mpris_player = MPRIS(bus_name)
    mpris_player.setUpdateHandler(on_player_update)

    print("Initializing display")

    display = Display()

    print("Initializing buttons: {}".format(list(Button)))

    buttons = Buttons()

    on_player_update()
    buttons.setButtonHandler(on_button_pressed)

    print("Init complete, press Ctrl+C to exit")

    signal.signal(signal.SIGINT, end)

    try:
        loop = GLib.MainLoop()
        loop.run()
    finally:
        buttons.cleanup()


if __name__ == '__main__':
    main()
