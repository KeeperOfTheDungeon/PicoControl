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
		
class PicoLedSet(ComponentSet):
	def __init__(self, components, protocol):
        pass
    
    
    def process():
        for component in self._component_list:
            component.process()
        
    
"""		actors = list()

		for component in components:
			actor = PicoLed(component)
			actors.append(actor)
		
		super().__init__(actors)
"""