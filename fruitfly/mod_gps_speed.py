# Based on code by Dan Mandle http://dan.mandle.me September 2012
# License: GPL 2.0

#3rd party
import gps
import fruitfly
from gps import *
from time import *

#stdlib
import os
import time
import threading
import random
import math

gpsd = None #seting the global variable

os.system('clear') #clear the terminal (optional)

class GpsPoller(threading.Thread):

    _gspd = None

    def __init__(self):
        threading.Thread.__init__(self)
        self._gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
        self.current_value = None
        self.daemon = True
        self.running = True #setting the thread running to true

    def run(self):
        while self.running:
            print("getting data")
            self._gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

    def get_speed(self):
        return self._gpsd.fix.speed

class gps_speed(fruitfly.Module):
    """A Fruitfly module that interfaces with a GPS module over USB"""

    _gps_thread = None
    _last_speed = 0


    def init(self):
        # Called by Fruitfly. 
        self._gps_thread = GpsPoller()
        try:
            self._gps_thread.start()
        except Exception as ex:
            print(ex)
   
    @fruitfly.repeat(0.1)
    def _poll(self):
        #See if we have changed speed

        current_speed = self._last_speed
        try:
            current_speed = self._gps_thread.get_speed()
            #current_speed = float(random.randint(0, 25)) / 10
        except Exception as ex:
            print(ex)

        if not math.isnan(current_speed) and current_speed != self._last_speed:
            self.send_event("speed_change", current_speed)
        
        self._last_speed = current_speed
 
