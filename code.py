'''
This project was inspired by Dave's Garage 'Live' coding of a analog clock
displaying on his LED display.
I do not have his display or hardware.
I do have a MagTag collecting dust.
Most of this is a direct copy form my M4 Matrix Portal
Noteable changes:
  Backgroud color is set to white
  All other colors are black. You know... e-ink

References:
Dave's Garage: https://www.youtube.com/watch?v=yIpdBVu9xv8
Various Adafruit howto's, API documentation and *gasp* looking at various Adafruit git repos.

All mistakes are my fault.
'''
import time
import math
import board
import displayio
#https://docs.circuitpython.org/projects/magtag/en/latest/index.html
from adafruit_magtag.magtag import MagTag
from adafruit_magtag.network import Network
#https://docs.circuitpython.org/projects/display-shapes/en/latest/index.html
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line

BLACK  = 0x000000
WHITE  = 0xFFFFFF
WIDTH  = 32
HEIGHT = 32
centerX = centerY = radius = 0
HOUR = 0
MIN  = 0
SEC  = 0
HOURS_PASSED = 0
network = None

'''
Get wifi details and more from a secrets.py file
Required fileds
  - ssid
  - password
  - timezone
  - aio_username
  - aio_key
'''
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

'''
Draw the big clock circle
'''
def drawClockCircle(output):
    circle = Circle(centerX, centerY, radius, fill=None, outline=BLACK )
    output.append(circle)

'''
Draw the center circle
'''
def drawClockCenter(output):
    radius = 1
    circle = Circle(centerX, centerY, radius, fill=None, outline=BLACK)
    output.append(circle)

'''
Draw each of the tics around the clock face
'''
def drawClockHourTics(output):
  z = 0
  while z < 360:
    angle = math.radians(z)
    x2 = int( centerX + (math.sin(angle) * radius) )
    y2 = int( centerY - (math.cos(angle) * radius) )
    x3 = int( centerX + (math.sin(angle) * (radius-10) ) )
    y3 = int( centerY - (math.cos(angle) * (radius-10) ) )

    line = Line( x2, y2, x3, y3, BLACK )
    output.append( line )

    z += 30

'''
Draw the minute hand
'''
def drawClockMinHand( output ):
    angle = math.radians(MIN * 6)
    x2 = int( centerX + (math.sin(angle) * (radius-15) ) )
    y2 = int( centerY - (math.cos(angle) * (radius-15) ) )
    line = Line( centerX, centerY, x2, y2, BLACK )
    output.append( line )

def drawClockHourHand( output ):
    #HOUR can be up to 24 but the math still works because its a circle.
    angle = math.radians(HOUR * 30 + int(MIN/12*6))
    x2 = int( centerX + (math.sin(angle) * (radius/2) ) )
    y2 = int( centerY - (math.cos(angle) * (radius/2) ) )
    line = Line( centerX, centerY, x2, y2, BLACK )
    output.append( line )

def drawClock(display):
  global HOUR
  global MIN
  global SEC
  global HOURS_PASSED
  global network
  curr_time = time.localtime()

  if curr_time.tm_hour != HOUR:
      HOURS_PASSED += 1
  if HOURS_PASSED > 12:
      network.get_local_time()
      HOURS_PASSED = 0

  HOUR = curr_time.tm_hour
  MIN  = curr_time.tm_min
  SEC  = curr_time.tm_sec
  #print("Current time: %d:%d:%d" % (curr_time.tm_hour, curr_time.tm_min, curr_time.tm_sec) )

  splash = displayio.Group()
  display.show(splash)

  # Make a background color fill
  color_bitmap = displayio.Bitmap(display.width, display.height, 1)
  color_palette = displayio.Palette(1)
  color_palette[0] = WHITE
  bg_sprite = displayio.TileGrid(color_bitmap, x=0, y=0, pixel_shader=color_palette)
  splash.append(bg_sprite)

  drawClockCircle(splash)
  drawClockCenter(splash)
  drawClockHourTics(splash)
  drawClockMinHand(splash)
  drawClockHourHand(splash)

def connectNetwork():
    global network
    #this creates a network object but does not actually connect
    network = Network()
    attempt = 0
    while not network._wifi.is_connected:
        try:
            network.connect()
        except ConnectionError as e:
            print("could not connect to AP, retrying: ", e)
            continue
    network.get_local_time()

def main():
  global WIDTH
  global HEIGHT
  global centerX
  global centerY
  global radius

  magtag = MagTag()
  display = magtag.display

  WIDTH = display.width
  HEIGHT = display.height
  centerX = int((WIDTH-1)/2)
  centerY = int((HEIGHT-1)/2)
  radius = min(centerX, centerY)
  drawClock(display)

  connectNetwork()

  drawClock(display)

  while display.time_to_refresh > 0:
    print("Cannot refresh the display: %d" % (display.time_to_refresh))
    sleep(.1)
  display.refresh()

  while True:
    magtag.exit_and_deep_sleep(60)
    drawClock(display)

    while display.time_to_refresh > 0:
      print("Cannot refresh the display: %d" % (display.time_to_refresh))
      time.sleep(.1)
    display.refresh()

if __name__ == "__main__":
    main()
