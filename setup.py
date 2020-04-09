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
              'pidi-mpris=pidi_mpris.main:main'
          ]
      },
      data_files=[
          ('/usr/share/pidi-mpris/images', [
              'data/images/luana-de-marco-PF1l1F1hzoU-unsplash.png',
              'data/images/deployrainbows.gif',
              'data/images/LICENSE.txt'
          ]),
          ('/usr/share/pidi-mpris/fonts/OpenSans', [
              'data/fonts/OpenSans/OpenSans-Bold.ttf',
              'data/fonts/OpenSans/OpenSans-BoldItalic.ttf',
              'data/fonts/OpenSans/OpenSans-ExtraBold.ttf',
              'data/fonts/OpenSans/OpenSans-ExtraBoldItalic.ttf',
              'data/fonts/OpenSans/OpenSans-Italic.ttf',
              'data/fonts/OpenSans/OpenSans-Light.ttf',
              'data/fonts/OpenSans/OpenSans-LightItalic.ttf',
              'data/fonts/OpenSans/OpenSans-Regular.ttf',
              'data/fonts/OpenSans/OpenSans-SemiBold.ttf',
              'data/fonts/OpenSans/OpenSans-SemiBoldItalic.ttf',
              'data/fonts/OpenSans/LICENSE.txt'
          ]),
          ('/etc', ['conf/pidi-mpris.conf'])
      ],
      python_requires='>=3.6')
