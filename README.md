# colorrise

Colorrise is a tiny flask server for sending a color via the web to a raspberry pi controlling some neopixel LEDs.

It depends on:
- http://flask.pocoo.org
- https://github.com/mikest/rpi_ws281x
- https://pypi.python.org/pypi/colour

The Flask server responds to request of the form `set?color=#ffFFff`
