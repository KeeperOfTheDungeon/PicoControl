from RoboControl.Robot.Component.Actor.Led import Led, LedSet
from machine import Pin

class LedPico:
    def __init__(self,led, pin):
         self._led = led
         self._pin = Pin(pin, Pin.OUT)
         self._pin.on()
         
    def set_brightness(self, brightness):
        self._led.set_brightness(brightness)
        
        if brightness < 0.5:
            self._pin.on()
        else:
            self._pin.off()


class LedSetPico(LedSet):
    def __init__(self, components, pin_list, protocol):
        super().__init__(components, protocol)
        print("init ledPico Set")    
        self._ledList = list()
        
        for component, pin in zip(self,pin_list): 
            self._ledList.append(LedPico(component, pin))
            
          
    def set_brightness(self, index, brightness):
        self._ledList[index].set_brightness(brightness)