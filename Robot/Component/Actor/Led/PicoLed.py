from RoboControl.Robot.Component.Actor.Led import Led
from machine import Pin

class PicoLed(Led):
    
    def __init__(self, meta_data):
		super().__init__(meta_data)
		self._pin = meta_data["pin"]
		self._led = Pin(self._pin, Pin.OUT)
		
		
	def process():
        if self._brightness_value > 0:
            self._led.on()
        else:
            self._led.off()
        
        
        pass