import argparse
import signal
import sys

from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop

from .mpris import find_available_players, MPRIS
from .display import Display


def on_player_update():
    global display, player
    artUrl = player.artUrl()
    if artUrl.startswith('file://'):
        display.set(artUrl[len('file://'):])


def end(_signal, _frame):
    global loop
    print('Ctrl+C captured, exiting program.')
    loop.quit()


if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

    parser = argparse.ArgumentParser(description="Pirate Audio MPRIS")
    parser.add_argument('-n', '--name', default=None,
                        help="Bus name of the media player (has to start with 'org.mpris.MediaPlayer2.')")

    args = parser.parse_args()

    mpris_players = find_available_players()
    bus_name = args.name
    if bus_name is None and len(mpris_players) > 0:
        bus_name = mpris_players[0]

    if bus_name is None or bus_name not in mpris_players:
        print("Unable to find MPRIS player '{}'".format(bus_name))
        sys.exit(1)

    print("Connecting to MPRIS player '{}'".format(bus_name))

    player = MPRIS(bus_name)
    player.updateHandler = on_player_update

    display = Display()
    on_player_update()

    signal.signal(signal.SIGINT, end)

    loop = GLib.MainLoop()
    loop.run()
