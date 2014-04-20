import fruitfly
import wave
import alsaaudio
import time

class play(fruitfly.Module):
    """A Fruitfly module that plays a sound on keypresses"""
    
    #Soundcard device
    _device = None

    #Sound playback settings
    CHANNELS = 2 #mono
    BPF = 2 #bytes per frame
    SAMPLE_RATE = 44100 #aka sampling rate, in Hz 
    PERIOD_SIZE = 44 * BPF * CHANNELS #bytes per millisecond, every frame is two bytes

    _current_sound = None

    _last_key = None

    def _setup_device(self):
        card = 'default'
        self._device = alsaaudio.PCM(card=card, mode=alsaaudio.PCM_NORMAL)
        self._device.setchannels(self.CHANNELS)
        self._device.setrate(self.SAMPLE_RATE)
        self._device.setformat(alsaaudio.PCM_FORMAT_S16_LE) #signed data, little endian
        self._device.setperiodsize(self.PERIOD_SIZE) #amount of data to be played at once


    @fruitfly.event("keyup")
    def select_sound(self, _, keycode):
        key = keycode[1]
        if key in self.config:
            if key == self._last_key and self._current_sound:
                # If it's the same key, stop playing
                self._stop_sound()
            elif self._current_sound:
                # If something was already playing, interrupt it 
                self._stop_sound()
                self._start_sound(self.config[key])
            else:
                # Play sound
                self._start_sound(self.config[key])
        self._last_key = key

    @fruitfly.repeat(0.001) # every millisecond
    def pump_sound_data(self):
        if self._current_sound:
            # Connect soundcard if required.
            if self._device is None:
                self._setup_device()
            data = self._current_sound.readframes(self.PERIOD_SIZE)
            if data:
                #pass
                self._device.write(data)
            else:
                self._stop_sound()
        else:
            # Can't disconnect from Fruitfly, so this is a workaround to 
            # reduce processor usage
            time.sleep(0.05)

    def _start_sound(self, filename):
        self._current_sound = wave.open(filename, 'rb')
        self.pump_sound_data() #prefill the buffer a little

    def _stop_sound(self):
        self._current_sound.close();
        self._current_sound = None;
        
