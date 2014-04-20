import fruitfly

# Generates 'wubwubwub' noise that varies with speed, for use on an art car.

# stdlib
import sys
import wave
import getopt
import math, array, random, io
import time
import os
import struct

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
    _changed_parameter = True
    _volume = 3 #as a level
    MAX_VOLUME = 3

    def init(self):
        # Called by Fruitfly
        self._sound_bank = self._locate_and_modify_sounds(self.MAX_SPEED)
        self._device = self._setup_device()
        self._select_sound()

    @fruitfly.repeat(PUMP_DURATION)
    def _pump_sound(self): 
        """Play the next chunk of the current stream."""
        if self._changed_parameter:
            self._select_sound()

        if self._current_sound:
            data_chunk = self._current_sound.readframes(self.FRAMES_PER_PUMP ) #string of bytes
            if data_chunk:
                self._device.write(data_chunk)
            else:
                self._select_sound()

    def _select_sound(self):
        if self._changed_parameter:
            self._changed_parameter = False
            
            #load new sound
            if self._current_sound:
                self._current_sound = None

            if self._speed > 0:
                #self._current_sound = self._sound_bank[self._speed -1]
                self._current_sound = self._sound_bank[self._speed -1][self._volume]
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


    def _locate_and_modify_sounds(self, n_sounds):
        """Find wum samples and preload them as streams"""
        sounds = []
        for speed in range(1, n_sounds+1): # speed 0 = no sound
            filename = os.path.join(self.config['samples'], 'wum' + str(speed) + '.wav')
            print(filename)
            original_wave = wave.open(filename, 'rb')
            original_stream = original_wave.readframes(self.FRAME_RATE * self.FRAME_DURATION)


            volumes = []
            for volume in range(0, self.MAX_VOLUME + 1):
                print("building volume", volume)

                fmt = 'h' * (self.FRAME_RATE * self.FRAME_DURATION)
                values = struct.unpack(fmt, original_stream)
                values = map(lambda sample: int(float(sample) * (float(volume) / self.MAX_VOLUME)) , values)
                data_chunk_modified = struct.pack(fmt, *values)

                modified_stream = io.BytesIO()
                modified_wave = wave.open(modified_stream, 'w')
                modified_wave.setparams((self.CHANNELS, self.BPS, self.FRAME_RATE, self.FRAME_RATE * self.FRAME_DURATION, "NONE", "Uncompressed"))
                modified_wave.writeframes(data_chunk_modified)
                modified_wave.close()
                modified_stream.seek(0)
               
                volumes.append(wave.open(modified_stream, 'rb'))
            sounds.append(volumes)    
            #TODO: fail gracefully if a sample is missing
        
            original_wave.close()
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
    def _set_volume(self, _, keycode):
        print("wum sees keyup")
        key = keycode[1]
        if key == "on":
            if self._speed < self.MAX_SPEED:
                pass
                #self._speed += 1
                #self._changed_parameter = True
            if self._volume < self.MAX_VOLUME:
                self._volume += 1 
                self._changed_parameter = True
        elif key == "off":
            if self._speed > 0:
                pass
                #self._speed -= 1
                #self._changed_parameter = True
            if self._volume > 0:
                self._volume -= 1
                self._changed_parameter = True
        print(self._volume)

      
