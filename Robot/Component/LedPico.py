from RoboControl.Robot.Component.Actor.Led import Led, LedSet
from machine import Pin

class LedPico:
    def __init__(self,led, pin):
         print(led, " : ", pin)
         self._led = led
         self._pin = Pin(pin, Pin.OUT)
         self._pin.on()
         
    def set_brightness(self, brightness):
        print(self._led)
        if brightness < 0.5:
            self._pin.on()
            print("off")
        else:
            self._pin.off()
            print("on")

class LedSetPico(LedSet):
    def __init__(self, components, protocol):
        super().__init__(components, protocol)
        print("create ledPico Set")    
        self._ledList = list()
        
        pinlist =[18,19,20,21,22,23]
        
        for component, pin in zip(self,pinlist): 
            self._ledList.append(LedPico(component, pin))
            
        print(len(self._ledList))
        
        for component in self._ledList:
            print(component)
            
    def set_brightness(self, index, brightness):
        self._ledList[index].set_brightness(brightness)