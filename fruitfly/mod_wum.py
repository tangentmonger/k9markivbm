import fruitfly

# Generates 'wubwubwub' noise that varies with speed, for use on an art car.

# stdlib
import sys
import wave
import getopt
import math, array, random, io
import time
import os

# third party
import alsaaudio



class wum(fruitfly.Module):
    """A Fruitfly module that generates continuous wum noise"""

    #Sound playback settings
    CHANNELS = 1 #mono, ie 1 sample per frame
    FRAME_RATE = 44100 #aka sampling rate, in Hz 
    BPS = 2 #bytes per samples
    FRAME_DURATION = 1 #in seconds
    PUMP_DURATION = 0.1 # in seconds
    FRAMES_PER_PUMP =  int(FRAME_RATE * FRAME_DURATION * PUMP_DURATION * BPS) 

    #Art car settings
    MAX_SPEED = 5
    _speed = 1

    _sound_bank = None
    _device = None
    _current_sound = None
    _changed_speed = True

    def init(self):
        # Called by Fruitfly
        print("FPP=", self.FRAMES_PER_PUMP)
        self._sound_bank = self._locate_sounds(self.MAX_SPEED)
        self._device = self._setup_device()
        self._select_sound()

    @fruitfly.repeat(PUMP_DURATION)
    def _pump_sound(self): 
        """Play the next chunk of the current stream."""
        if self._changed_speed:
            self._select_sound()

        if self._current_sound:
            dataChunk = self._current_sound.readframes(self.FRAMES_PER_PUMP )
            if dataChunk:
                self._device.write(dataChunk)
            else:
                self._select_sound()

    def _select_sound(self):
        if self._changed_speed:
            self._changed_speed = False
            
            #load new sound
            if self._current_sound:
                self._current_sound.close()
                self._current_sound = None

            if self._speed > 0:
                current_stream = self._sound_bank[self._speed-1]
                #current_stream.seek(0)
                #self._current_sound = wave.open(current_stream, 'rb')
                self._current_sound = self._sound_bank[self._speed -1]
                self._current_sound.rewind()
                
                print("nfraems as read", self._current_sound.getnframes())
                self._pump_sound() #preload buffer a bit

        else:
            #reload previous sound
            if self._speed > 0:
               self._current_sound.rewind()
               self._pump_sound() #preload buffer
        
    def _locate_sounds(self, n_sounds):
        """Find wum samples and preload them as streams"""
        sounds = []
        for speed in range(1, n_sounds+1): # speed 0 = no sound
            filename = os.path.join(self.config['samples'], 'wum' + str(speed) + '.wav')
            print(filename)
            sounds.append(wave.open(filename, 'rb'))    
            #TODO: fail gracefully if a sample is missing
        return sounds

                
    def _setup_device(self):
        card = 'default'
        device = alsaaudio.PCM(card=card, mode=alsaaudio.PCM_NORMAL)
        device.setchannels(self.CHANNELS)
        device.setrate(self.FRAME_RATE)
        device.setformat(alsaaudio.PCM_FORMAT_S16_LE) #signed data, little endian
        device.setperiodsize(int(self.FRAMES_PER_PUMP)) #amount of data to be played at once
        return device


    @fruitfly.event("keyup")
    def _set_speed(self, _, keycode):
        print("wum sees keyup")
        '''Temporary'''
        key = keycode[1]
        if key == 82:
            if self._speed < self.MAX_SPEED:
                self._speed += 1
                self._changed_speed = True
                #if self._speed == 1: #ie sound turns back on
                #self._select_sound()
        elif key == 81:
            if self._speed > 0:
                self._speed -= 1
                self._changed_speed = True
                #self._select_sound()

    def _get_speed(self):
        """Placeholder for something that gets art car speed"""
        speed = int(self.MAX_SPEED / 2)
        #while True:
        speed = (speed + (random.randint(-2,2))) % self.MAX_SPEED
        #yield speed
        return self._speed
        

       
