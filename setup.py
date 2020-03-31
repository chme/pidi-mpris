#!/usr/bin/env python

from distutils.core import setup

setup(name='pidi-mpris',
      version='0.0.1',
      description='MPRIS support for Pirate Audio',
      install_requires=['dbus-python', 'st7789', 'spidev', 'RPi.GPIO'],
      packages=['pidi_mpris'],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX :: Linux",
      ])
