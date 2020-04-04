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
    global display, player

    print("Player update: {} - {} - {}, artwork={}".format(player.albumArtist(), player.album(), player.title(), player.artUrl()))

    artUrl = player.artUrl()
    if artUrl.startswith('file://'):
        display.set(artUrl[len('file://'):])


def on_button_pressed(button):
    global player

    print("Button press detected: {}".format(button))

    if button == Button.A:
        # player.previous()
        pass
    elif button == Button.B:
        # player.next()
        pass
    elif button == Button.X:
        pass
    elif button == Button.Y:
        # player.playPause()
        pass


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


if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

    args = parse_arguments()

    bus_name = find_mpris_bus_name(args.name)
    if bus_name is None:
        print("Unable to find MPRIS player '{}'".format(args.name))
        sys.exit(1)

    print("Connecting to MPRIS player '{}'".format(bus_name))

    player = MPRIS(bus_name)
    player.setUpdateHandler(on_player_update)

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
