from setuptools import setup

setup(name='pidi-mpris',
      version='1.0.0',
      description='Control MPRIS media players with Pirate Audio Raspberry Pi Hat',
      author="Christian Meffert",
      author_email="christian.meffert@googlemail.com",
      url='https://github.com/chme/pidi-mpris',
      install_requires=['dbus-python', 'st7789',
                        'spidev', 'RPi.GPIO', 'pillow', 'numpy'],
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
              'data/images/namroud-gorguis-FZWivbri0Xk-unsplash.jpg',
              'data/images/simon-noh-0rmby-3OTeI-unsplash.jpg',
              'data/images/deployrainbows.gif',
              'data/images/LICENSE.md'
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
