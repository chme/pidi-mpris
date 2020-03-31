
import dbus
import re


class MPRIS:
    BUS_NAME_PREFIX = "org.mpris.MediaPlayer2."
    OBJECT_PATH = "/org/mpris/MediaPlayer2"
    INTERFACE_PLAYER = "org.mpris.MediaPlayer2.Player"
    INTERFACE_PROPERTIES = "org.freedesktop.DBus.Properties"

    def __init__(self, bus_name):
        self.bus_name = bus_name

        bus = get_bus()

        self.mpris = bus.get_object(self.bus_name, MPRIS.OBJECT_PATH)
        self.properties = dbus.Interface(
            self.mpris, MPRIS.INTERFACE_PROPERTIES)
        self.interface = dbus.Interface(self.mpris, MPRIS.INTERFACE_PLAYER)
        self.metadata = self.mpris.Get(
            MPRIS.INTERFACE_PLAYER, 'Metadata', dbus_interface=MPRIS.INTERFACE_PROPERTIES)

        self.updateHandler = None
        self.properties.connect_to_signal('PropertiesChanged', self.update)

    def update(self, *args):
        if len(args) > 1 and args[0] == MPRIS.INTERFACE_PLAYER and 'Metadata' in args[1]:
            self.metadata = args[1]['Metadata']
            if self.updateHandler:
                self.updateHandler()

    def playPause(self):
        self.interface.PlayPause()

    def next(self):
        self.interface.Next()

    def previous(self):
        self.interface.Previous()

    def length(self):
        return self.metadata['mpris:length']

    def artUrl(self):
        return self.metadata['mpris:artUrl']

    def album(self):
        return self.metadata['xesam:album']

    def albumArtist(self):
        return self.metadata['xesam:albumArtist']

    def artist(self):
        return self.metadata['xesam:artist']

    def title(self):
        return self.metadata['xesam:title']


def get_bus():
    try:
        bus = dbus.SessionBus()
    except dbus.exceptions.DBusException:
        bus = dbus.SystemBus()
    return bus


def find_available_players():
    bus = get_bus()
    return list(filter(lambda service: re.match(MPRIS.BUS_NAME_PREFIX, service), bus.list_names()))