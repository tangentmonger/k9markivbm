import fruitfly

# Uses https://pypi.python.org/pypi/pyusb
import usb

class usbhid(fruitfly.Module):
    """A Fruitfly module that claims a USB keyboard and generates key
    press and release events."""

    # USB HID devices tend to use USB endpoint 0x81.
    _endpoint = 0x81

    # A set of keys currently pressed by meaty fingers.
    _keyspressed = set()

    _device = None
    _handle = None

    def _setup(self):
        """Locates and opens the keyboard whose vendor/product IDs are
        defined in the config."""
        self._device = self._getDevice(self.config['vendor'], 
            self.config['product'])

        self._handle = self._openDevice(self._device)

    def _getDevice(self, vendor, product):
        """Search all devices on all USB busses for the specified vendor
        and product IDs."""
        for bus in usb.busses():
            for device in bus.devices:
                if device.idVendor == vendor and \
                    device.idProduct == product:
                        return device

    def _openDevice(self, device):
        """Open the device, detach the kernel's HID driver if attached, and
        claim the first interface. After that, the device is ready to use."""   
        handle = device.open()
        try:
            handle.detachKernelDriver(0)
        except:
            # Ignore failures here, the device might already be detached.
            pass

        handle.claimInterface(0)
        return handle

    @fruitfly.repeat(0.01)
    def poll(self):
        """Regularly checks for key data from the keyboard and generates 
        Fruitfly events for individual key presses and releases."""

        # If the keyboard isn't connected/available, try to do that.
        if self._device is None or self._handle is None:
            self._setup()

        # Try to read 8 bytes from the keyboard, with a 1s timeout.
        data = None
        try:
            data = self._handle.interruptRead(self._endpoint, 8, 1000)
        except usb.USBError as ex:
            # Py2 vs 3 compatibility
            message = ex.strerror or ex.message
            if message not in ["Operation timed out", \
                "could not detach kernel driver from interface 0: No data available", \
                "No error"]:
                # The above errors are harmless, but for others we should
                # discard the device/handle objects and try to reopen it.
                self._handle = None
                self._device = None
                raise # Re-raise to get it logged.

        if data is not None:
            # Parse data and generate appropriate key up/down events.
            modifiers = data[0]
            keys = list(data[2:8])

            # "To obtain a special dialling wand, please mash the keypad
            # with your palm now." (The Simpsons, Season 7, Episode 5)
            if keys == [1, 1, 1, 1, 1, 1]:
                # Too many keys pressed at once, ignore this event.
                self.send_event("keyerror", "too many keys pressed")
                return

            # See which keys are pressed right now.
            keyspressed = set(filter(lambda k: k != 0, keys))

            # Send keydown events for any new keys.
            for keycode in keyspressed.difference(self._keyspressed):
                label = self._getLabel(keycode)
                self.send_event("keydown", (modifiers, label, keycode))

            # Send keyup events for any released keys.
            for keycode in self._keyspressed.difference(keyspressed):
                label = self._getLabel(keycode)
                self.send_event("keyup", (modifiers, label, keycode))

            # Store set of pressed keys for next time.
            self._keyspressed = keyspressed
    
    def _getLabel(self, keycode):
        """Given a numeric `keycode`, returns a short string label for
        that the keycode maps to. Mappings are defined in the config.
        Returns None if there is no label for a keycode."""
        try:
            return self.config['labelmap'][keycode]
        except KeyError:
            return None

    def __del__(self):
        self._handle.releaseInterface()
