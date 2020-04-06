
import dbus
import re


class MPRIS:
    BUS_NAME_PREFIX = 'org.mpris.MediaPlayer2.'
    OBJECT_PATH = '/org/mpris/MediaPlayer2'
    INTERFACE_PLAYER = 'org.mpris.MediaPlayer2.Player'
    INTERFACE_PROPERTIES = 'org.freedesktop.DBus.Properties'

    def __init__(self, bus_name):
        self.bus_name = bus_name

        self.bus = get_bus()
        self.busObject = self.bus.get_object("org.freedesktop.DBus",
                                             "/org/freedesktop/DBus")
        self.busObject.connect_to_signal(
            "NameOwnerChanged", self.nameOwnerChanged)

        self.updateHandler = None

    def nameOwnerChanged(self, name, _oldOwner, newOwner):
        if name == self.bus_name:
            if newOwner:
                self.connect()
            else:
                self.disconnect()

    def connect(self):
        print('Connecting to MPRIS player {}'.format(self.bus_name))

        self.mpris = self.bus.get_object(self.bus_name, MPRIS.OBJECT_PATH)
        self.properties = dbus.Interface(
            self.mpris, MPRIS.INTERFACE_PROPERTIES)
        self.interface = dbus.Interface(self.mpris, MPRIS.INTERFACE_PLAYER)
        self.metadata = self.mpris.Get(
            MPRIS.INTERFACE_PLAYER, 'Metadata', dbus_interface=MPRIS.INTERFACE_PROPERTIES)

        self.properties.connect_to_signal(
            'PropertiesChanged', self.propertiesChanged)

    def disconnect(self):
        print('Disconnecting from MPRIS player {}'.format(self.bus_name))

        self.mpris = None
        self.properties = None
        self.interface = None
        self.metadata = {}

    def propertiesChanged(self, *args):
        if len(args) > 1 and args[0] == MPRIS.INTERFACE_PLAYER and 'Metadata' in args[1]:
            self.metadata = args[1]['Metadata']
            if self.updateHandler:
                self.updateHandler()

    def setUpdateHandler(self, cb):
        self.updateHandler = cb

    def playPause(self):
        if self.interface:
            self.interface.PlayPause()

    def next(self):
        if self.interface:
            self.interface.Next()

    def previous(self):
        if self.interface:
            self.interface.Previous()

    def length(self):
        return self.metadata.get('mpris:length', 0)

    def artUrl(self):
        return self.metadata.get('mpris:artUrl', '')

    def album(self):
        return self.metadata.get('xesam:album', '')

    def albumArtist(self):
        return self.metadata.get('xesam:albumArtist', [])

    def artist(self):
        return self.metadata.get('xesam:artist', [])

    def title(self):
        return self.metadata.get('xesam:title', '')


def get_bus():
    try:
        bus = dbus.SessionBus()
    except dbus.exceptions.DBusException:
        bus = dbus.SystemBus()
    return bus


def find_available_players():
    bus = get_bus()
    return list(filter(lambda service: re.match(MPRIS.BUS_NAME_PREFIX, service), bus.list_names()))
