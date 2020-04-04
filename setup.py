from setuptools import setup

setup(name='pidi-mpris',
      version='0.0.1',
      description='MPRIS support for Pirate Audio',
      install_requires=['dbus-python', 'st7789', 'spidev', 'RPi.GPIO'],
      packages=['pidi_mpris'],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX :: Linux",
      ],
      entry_points={
          'console_scripts': [
              'pidi-mpris=pidi_mpris.player:main'
          ]
      },
      python_requires='>=3.6')
