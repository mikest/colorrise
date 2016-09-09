#!/usr/bin/python
# Color-Rise
# (C) 2016 Mike Estee, MIT License

import time
from colour import Color
from flask import Flask, render_template, request
import threading

# https://github.com/jgarff/rpi_ws281x
import _rpi_ws281x as ws
import neopixel

# https://api.forecast.io/forecast/57fe5197b6b5632dbe542ff8c1cae6ba/37.8267,-122.423
import forecastio

api_key = "your_key_goes_here"
lat = 37.8267
lng = -122.423


# LED strip configuration:
LED_COUNT      = 48      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 1     # Set to 0 for darkest and 1 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

# global settings for lighting strip
pixels = []
brightness = LED_BRIGHTNESS
strip = neopixel.Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
			LED_INVERT, LED_BRIGHTNESS*200, 0, ws.WS2811_STRIP_GRB)

def sync_pixels():
	strip.setBrightness(brightness*200)
	n = 0
	for c in pixels:
		if isinstance(c, Color) and n<LED_COUNT:
			strip.setPixelColorRGB(n, int(c.red*255), int(c.green*255), int(c.blue*255))
			n += 1
	strip.show()


# Background updating thread for pixels
class PixelThread(object):
	def __init__(self, interval=500):
		self.interval = interval
		thread = threading.Thread(target=self.run, args=())
		thread.daemon = True
		thread.start()

	def run(self):
		# continuously update our colors forever
		while True:
			#sync_pixels()
			time.sleep(self.interval/1000.0)



def map(index):
	"""Translate index positions to pixel positions"""
	index += 2			#first two are blocked
	index = (LED_COUNT - index)-1	#invert rotation
	index -= (LED_COUNT - 2) / 2
	index = index + (LED_COUNT-2) if index < 2 else index	# wrap
	return index

def localHour():
	hour = time.localtime().tm_hour
	return hour

def isMorning():
	hour = localHour()
	if hour >= 6 and hour <= 9:
		return True
	else:
		return False

def isBedtime():
	hour = localHour()
	if hour >= (12+8) or hour <= 5:
		return True
	else:
		return False


# Main program logic follows:
app = Flask(__name__)

@app.route("/set", methods=['GET'])
def set_color():
	global pixels
	cstr = request.args['color']
	try:
		color = Color(cstr)
	except:
		print "unknown color:" + cstr
		return cstr, 200

	for n in range(0,LED_COUNT):
		pixels[n] = color

	sync_pixels()
	return cstr, 200

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

@app.route("/")
def home():
	templateData = {
		'time': 'now'
	}
	return render_template('home.html', **templateData)

# main
if __name__ == '__main__':
	
	# initial values for pixels
	for n in range(0, LED_COUNT):
		pixels.append( Color(hsl=(n/float(LED_COUNT),1,.5)) )
	strip.begin()
	sync_pixels()

	# start update background thread
	PixelThread()

	# start the flask server
	app.run(host='0.0.0.0', port=80, debug=True)
	exit()
	

	# start = time.clock() - 3600
	# color = Color(255,255,255)
	# colorMap = {
	# 	"clear-day"   : Color(255, 255, 102), # yellow
	# 	"clear-night" : Color(0, 0, 102), # dark blue
	# 	"rain" : Color(0, 153, 255), # light blue
	# 	"snow" : Color(255,255,255), #white
	# 	"sleet": Color(51, 102, 153), #dark gray blue
	# 	"wind" : Color(102, 153, 153), # gray green
	# 	"fog"  : Color(204, 204, 204), #light gray 
	# 	"cloudy" : Color(64, 64, 64), #dark gray
	# 	"partly-cloudy-day" : Color(128, 128, 100), #beige
	# 	"partly-cloudy-night" : Color(117, 117, 163), # gray purple
	# 	}

	# # if key not in dic:

	# while True:
	# 	current = time.clock()
	# 	if (current - start) > 3600:
	# 		start = current
	# 		forecast = forecastio.load_forecast(api_key, lat, lng)
	# 		byHour = forecast.hourly()

	# 		print "forecast for next 24 hours"
	# 		for hour in byHour.data:
	# 			print hour.icon + " " + str(hour.temperature)

	# 		# dim the lights for bedtime
	# 		brightness = LED_BRIGHTNESS
	# 		if isBedtime():
	# 			brightness = brightness/10
			
	# 		strip.setBrightness(brightness)
		
	# 	# set the forecast
	# 	pixels = len(byHour.data) / strip.numPixels();
	# 	#print "pixels:" + str(pixels)
	# 	mightRain = False
	# 	for i in range(0,len(byHour.data)):
	# 		hour = byHour.data[i]
			
	# 		# weather to color
	# 		skyColor = Color(0,0,0)
	# 		if hour.icon in colorMap:
	# 			skyColor = colorMap[hour.icon]

	# 		# will it rain today after 9am?
	# 		if (i%24) > 9 and hour.precipProbability > 10:
	# 			mightRain = True

	# 		# temp
	# 		temp = (hour.temperature - 30.) / 70.0
	# 		tempColor = Color(int(255*temp),0,int(255*(1.0-temp)) )

	# 		if mightRain and isMorning():
	# 			skyColor = Color(0,128,255)

	# 		for n in range(0,pixels):
	# 			strip.setPixelColor(map(i*pixels + n), skyColor )
	# 	strip.show()
	# 	time.sleep(2)
