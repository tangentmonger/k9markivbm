#! /usr/bin/python
# Generates a set of wum sounds of increasing intensity.
# For use with mod_wum.py

#stdlib
import math, array, random, io
import wave
import os

def generate_wum(path, n_sounds):
    
    """Pregenerates sound clips as streams for every speed setting"""
    
    volume = 100 # percent
    frames = int(FRAME_RATE * FRAME_DURATION)

    for speed in range(1, n_sounds+1):
        print("creating wum", speed)
        # Random Sound FX Using WAV File
        # http://en.wikipedia.org/wiki/Amplitude_modulation
        # http://en.wikipedia.org/wiki/Frequency_modulation
        # FB36 - 20120701
  
        # Assumed: ampCR = ampAM = ampFM = 1
        data = array.array('h') # signed short integer (-32768 to 32767) data
        
        #Use numbers that are factors of 4410 to reduce clicks between samples
        #1 2 3 5 6 7 9 10 14 15 18 21 30 35 42 45 49 63 70 90 98 105 126 147 210 245 294 315 441 490 630 735 882 1470 2205 4410
        
        freqCR = [15, 21,35, 42, 49, 63, 90, 105, 126, 147, 210, 245][speed] # random.randint(500, 3000) # frequency of the carrier wave (Hz) 
        freqAM = 98 #random.randint(1, 10) # frequency of the AM wave (Hz) 
        freqFM = [2, 3, 5,9,15,21,35, 42, 49, 63, 70][speed] #random.randint(1, 10) # frequency of the FM wave (Hz) 
        freqFMDev = 49 #random.randint(100, 400) # frequency deviation for FM (Hz) 
        phaseCR = 0 #random.random() * math.pi * 2
        phaseAM = 0 #random.random() * math.pi * 2
        phaseFM = 0 #random.random() * math.pi * 2
  
        # nSPC: number of Samples Per Cycle
        # if numbers are factors then these are already integers :)
        nSPCCR = int(FRAME_RATE / freqCR)
        nSPCAM = int(FRAME_RATE / freqAM)
        nSPCFM = int(FRAME_RATE / freqFM)
        for i in range(frames):
            #sample = 32767 * float(volume) / 100
            sample = float(2**((8 * BPS) - 1) - 1) * float(volume) / 100
            tCR = math.pi * 2 * (i % nSPCCR) / nSPCCR + phaseCR
            tFM = math.pi * 2 * (i % nSPCFM) / nSPCFM + phaseFM
            tAM = math.pi * 2 * (i % nSPCAM) / nSPCAM + phaseAM
            sample *= math.sin(tCR + math.sin(tFM) * freqFMDev / freqFM)
            sample *= (math.sin(tAM) + 1) / 2
            data.append(int(sample))
            
        filename = os.path.join(path, 'wum' + str(speed) + '.wav')
        print("creating ", filename)
        f = wave.open(filename, 'w')
        f.setparams((CHANNELS, BPS, FRAME_RATE, frames, "NONE", "Uncompressed"))
        f.writeframes(data.tostring())
        print("nframes", frames)
        print("data length of sample", len(data.tostring()))
        f.close

CHANNELS = 1 #mono, ie 1 sample per frame
FRAME_RATE = 44100 #aka sampling rate, in Hz 
BPS = 2 #bytes per samples
FRAME_DURATION = 1 #in seconds
PUMP_DURATION = 0.1 # in seconds
FRAMES_PER_PUMP =  int(FRAME_RATE * FRAME_DURATION * PUMP_DURATION * BPS) 



if __name__ == '__main__':
    generate_wum('samples/wum/', 10)
    
   
