from RoboControl.Robot.Component.Sensor.LightSensor import LightSensor, LightSensorSet
from machine import ADC
from machine import Timer





class LightSensorPico:
    def __init__(self,light_sensor, adc_channel):
         self._adc_channel = ADC(adc_channel)
         self._light_sensor = light_sensor
         print("add light Sensor")
         
    def test(self):
        value = float(self._adc_channel.read_u16())
        value /= 65535
        print(value)
        
"""    def set_brightness(self, brightness):
        self._led.set_brightness(brightness)
        
        if brightness < 0.5:
            self._pin.on()
        else:
            self._pin.off()
"""
    
    
    
class LightSensorSetPico(LightSensorSet):
    def __init__(self, components, channel_list, protocol):
        super().__init__(components, protocol)
        print("init lightPico Set")    
        self._lightSensorList = list()
        
        soft_timer = Timer(mode=Timer.PERIODIC, period=1000, callback=self.interruption_handler)
        
        for component, adc_channel in zip(self,channel_list): 
            self._lightSensorList.append(LightSensorPico(component, adc_channel))

        print(self)
        print("----")

    def interruption_handler(self, timer):
        print("Time!!!!!!!!!!!!!!r")
        self._lightSensorList[0].test()
