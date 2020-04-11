'''
The MIT License (MIT)

Copyright (c) 2020 Christian Meffert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import dbus
from enum import Enum
import logging


log = logging.getLogger(__name__)


class PlaybackStatus(Enum):
    PLAYING = 'Playing'
    PAUSED = 'Paused'
    STOPPED = 'Stopped'
    UNKNOWN = 'Unkown'


class MPRIS:
    BUS_NAME_PREFIX = 'org.mpris.MediaPlayer2.'
    OBJECT_PATH = '/org/mpris/MediaPlayer2'
    INTERFACE_PLAYER = 'org.mpris.MediaPlayer2.Player'
    INTERFACE_PROPERTIES = 'org.freedesktop.DBus.Properties'

    def __init__(self, bus_name):
        self.bus_name = bus_name
        self.connectedBus = None
        self.mpris = None
        self.properties = None
        self.interface = None

        self.metadata = {}
        self.status = PlaybackStatus.UNKNOWN

        self.bus = get_bus()
        self.busObject = self.bus.get_object("org.freedesktop.DBus",
                                             "/org/freedesktop/DBus")
        self.busObject.connect_to_signal(
            "NameOwnerChanged", self.nameOwnerChanged)

        self.updateHandler = None

        availablePlayer = self._find_mpris_bus_name(self.bus_name)
        if availablePlayer:
            self.connect(availablePlayer)

    def nameOwnerChanged(self, name, _oldOwner, newOwner):
        if not name.startswith(MPRIS.BUS_NAME_PREFIX):
            return

        log.debug('NameOwnerChange: %s/%s/%s', name, _oldOwner, newOwner)

        if self.connectedBus:
            if not newOwner and name == self.connectedBus:
                self.disconnect()
        else:
            if newOwner and self._busNameMatches(name):
                self.connect(name)

    def _busNameMatches(self, name):
        return (self.bus_name and name == self.bus_name) or (not self.bus_name and name.startswith(MPRIS.BUS_NAME_PREFIX))

    def _find_available_players(self):
        return list(filter(lambda service: service.startswith(MPRIS.BUS_NAME_PREFIX), self.bus.list_names()))

    def _find_mpris_bus_name(self, arg_bus_name):
        mpris_players = self._find_available_players()

        log.debug('Available MPRIS players: %s', mpris_players)

        if arg_bus_name is None:
            if len(mpris_players) > 0:
                return mpris_players[0]
            return None

        if arg_bus_name in mpris_players:
            return arg_bus_name
        return None

    def connect(self, busName):
        log.info('Connecting to MPRIS player %s', busName)

        self.mpris = self.bus.get_object(busName, MPRIS.OBJECT_PATH)
        self.properties = dbus.Interface(
            self.mpris, MPRIS.INTERFACE_PROPERTIES)
        self.interface = dbus.Interface(self.mpris, MPRIS.INTERFACE_PLAYER)
        self.metadata = self.mpris.Get(
            MPRIS.INTERFACE_PLAYER, 'Metadata', dbus_interface=MPRIS.INTERFACE_PROPERTIES)
        self.status = self.__toPlaybackStatus(self.mpris.Get(
            MPRIS.INTERFACE_PLAYER, 'PlaybackStatus', dbus_interface=MPRIS.INTERFACE_PROPERTIES))

        self.properties.connect_to_signal(
            'PropertiesChanged', self.propertiesChanged)

        self.connectedBus = busName

    def disconnect(self):
        log.info('Disconnecting from MPRIS player %s', self.bus_name)

        self.mpris = None
        self.properties = None
        self.interface = None
        self.metadata = {}

        self.connectedBus = None

    def propertiesChanged(self, *args):
        if len(args) <= 1 or args[0] != MPRIS.INTERFACE_PLAYER:
            return

        hasChanges = False
        if 'Metadata' in args[1]:
            self.metadata = args[1]['Metadata']
            hasChanges = True

        if 'PlaybackStatus' in args[1]:
            self.status = self.__toPlaybackStatus(args[1]['PlaybackStatus'])
            hasChanges = True

        log.debug('DBUS property changes %s (%s)', hasChanges, args[1])
        if hasChanges and self.updateHandler:
            self.updateHandler()

    def setUpdateHandler(self, cb):
        self.updateHandler = cb

    def playbackStatus(self):
        return self.status

    def __toPlaybackStatus(self, propValue):
        try:
            return PlaybackStatus(propValue)
        except ValueError:
            return PlaybackStatus.UNKNOWN

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
        log.info('Connected to DBUS session bus')
    except dbus.exceptions.DBusException:
        bus = dbus.SystemBus()
        log.info('Connected to DBUS system bus')
    return bus
