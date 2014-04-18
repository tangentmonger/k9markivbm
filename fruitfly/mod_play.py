import fruitfly
import wave
import alsaaudio

class play(fruitfly.Module):
    """A Fruitfly module that plays a sound every 3s"""
    
    #Soundcard device
    _device = None

    #Sound playback settings
    CHANNELS = 1 #mono
    SAMPLE_RATE = 44100 #aka sampling rate, in Hz 
    PERIOD_SIZE = 441


    def _setup_device(self):
        card = 'default'
        self._device = alsaaudio.PCM(card=card, mode=alsaaudio.PCM_NORMAL)
        self._device.setchannels(self.CHANNELS)
        self._device.setrate(self.SAMPLE_RATE)
        self._device.setformat(alsaaudio.PCM_FORMAT_S16_LE) #signed data, little endian
        self._device.setperiodsize(self.PERIOD_SIZE) #amount of data to be played at once


    @fruitfly.repeat(3) #seconds
    def play_sound(self): 
        # If the keyboard isn't connected/available, try to do that.
        if self._device is None:
            self._setup_device()

        """Play the supplied stream from the beginning."""
        g = wave.open("test.wav", 'rb')
        dataChunk = g.readframes(self.PERIOD_SIZE)
        while dataChunk:
            self._device.write(dataChunk)
            dataChunk = g.readframes(self.PERIOD_SIZE)
        g.close()


