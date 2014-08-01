#!/usr/bin/env python3

# Generates 'wubwubwub' noise that varies with speed, for use on an art car.

import sys
import wave
import getopt
import alsaaudio
import math, array, random, io
import time
        
def generate_sounds(n_sounds):
    """Pregenerates sound clips for every speed setting"""
    sounds = []
    
    dataSize = 2 # 2 bytes because of using signed short integers => bit depth = 16
    duration = 1 # seconds
    volume = 100 # percent
    numSamples = int(SAMPLE_RATE * duration)

    for speed in range(1, n_sounds+1):
        # Random Sound FX Using WAV File
        # http://en.wikipedia.org/wiki/Amplitude_modulation
        # http://en.wikipedia.org/wiki/Frequency_modulation
        # FB36 - 20120701
  
        # Assumed: ampCR = ampAM = ampFM = 1
        data = array.array('h') # signed short integer (-32768 to 32767) data
        stream = io.BytesIO()
        
        #Use numbers that are factors of 44100 to reduce clicks between samples
        freqCR = [50, 60, 70, 84, 98, 126, 140, 150, 175, 196, 225][speed] # random.randint(500, 3000) # frequency of the carrier wave (Hz) 
        freqAM = 100 #random.randint(1, 10) # frequency of the AM wave (Hz) 
        freqFM = [1,2,3,4,5,6,7,9,10,12,14,15,18][speed] #random.randint(1, 10) # frequency of the FM wave (Hz) 
        freqFMDev = 42 #random.randint(100, 400) # frequency deviation for FM (Hz) 
        phaseCR = 0 #random.random() * math.pi * 2
        phaseAM = 0 #random.random() * math.pi * 2
        phaseFM = 0 #random.random() * math.pi * 2
  
        # nSPC: number of Samples Per Cycle
        # if numbers are factors then these are already integers :)
        nSPCCR = int(SAMPLE_RATE / freqCR)
        nSPCAM = int(SAMPLE_RATE / freqAM)
        nSPCFM = int(SAMPLE_RATE / freqFM)
        for i in range(numSamples):
            sample = 32767 * float(volume) / 100
            tCR = math.pi * 2 * (i % nSPCCR) / nSPCCR + phaseCR
            tFM = math.pi * 2 * (i % nSPCFM) / nSPCFM + phaseFM
            tAM = math.pi * 2 * (i % nSPCAM) / nSPCAM + phaseAM
            sample *= math.sin(tCR + math.sin(tFM) * freqFMDev / freqFM)
            sample *= (math.sin(tAM) + 1) / 2
            data.append(int(sample))
            
        f = wave.open(stream, 'w')
        f.setparams((CHANNELS, dataSize, SAMPLE_RATE, numSamples, "NONE", "Uncompressed"))
        f.writeframes(data.tostring())
        print(len(data.tostring()))
        f.close

        sounds.append(stream)
    
    return sounds
             
def setup_device():
    card = 'default'
    device = alsaaudio.PCM(card=card, mode=alsaaudio.PCM_NORMAL)
    device.setchannels(CHANNELS)
    device.setrate(SAMPLE_RATE)
    device.setformat(alsaaudio.PCM_FORMAT_S16_LE) #signed data, little endian
    device.setperiodsize(PERIOD_SIZE) #amount of data to be played at once
    return device

def get_speed():
    """Placeholder for something that gets art car speed"""
    speed = int(MAX_SPEED / 2)
    while True:
        speed = (speed + (random.randint(-2,2))) % MAX_SPEED
        yield speed
        #yield 1
    

def play_sound(stream): 
    """Play the supplied stream from the beginning."""
    stream.seek(0)
    g = wave.open(stream, 'rb')
    dataChunk = g.readframes(441)
    while dataChunk:
        # Read data from stdin
        device.write(dataChunk)
        dataChunk = g.readframes(441)
    g.close()



if __name__ == '__main__':

    #Sound playback settings
    CHANNELS = 1 #mono
    SAMPLE_RATE = 44100 #aka sampling rate, in Hz 
    PERIOD_SIZE = 441

    #Art car settings
    MAX_SPEED = 10

    sound_bank = generate_sounds(MAX_SPEED)
    device = setup_device()

    for speed in get_speed():
        print(speed)
        play_sound(sound_bank[speed]) #preload buffer
