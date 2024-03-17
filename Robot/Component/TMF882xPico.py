from PicoControl.com.tmf8821.com.i2c_com import I2C_com
from PicoControl.com.tmf8821.tmf8821_app import Tmf8821App, TMF8821ResultFrame
from PicoControl.com.tmf8821.tmf8821_utility import Tmf8821Utility
from RoboControl.Robot.Component.Sensor.TMF882x import TMF882xSet, TMF882x, TMF882xDistanceSensor
from machine import Timer


class TMF882xPico:

    def __init__(self, sensor: TMF882x, i2c_addr):
        self._i2c_addr = i2c_addr
        self._sensor = sensor

        self.tof = Tmf8821Utility(
            ic_com=I2C_com()
        )

        print("Try to open TMF8821 connection")
        if Tmf8821App.Status.OK != self.tof.open():  # open FTDI communication channels
            raise RuntimeError("Error open FTDI device")
        else:
            print("Opened TMF8821 connection")

        self.tof.init_bootloader_check()

        soft_timer = Timer(mode=Timer.PERIODIC, period=10000, callback=self.measure)

    def measure(self, timer):
        frame: list[TMF8821ResultFrame] = self.tof.measure_frame()
        if frame is not None and len(frame) > 0:
            counter = 0
            sensors: list[TMF882xDistanceSensor] = self._sensor.get_distance_sensors()
            for sensor in sensors:
                if isinstance(sensor, TMF882xDistanceSensor):
                    sensor.set_distance(frame[0].results[counter])
                    counter += 1
                else:
                    self.tof._log("Sensor does not appear to be a TMF882x")


class TMF882xPicoSet(TMF882xSet):

    def __init__(self, components, i2c_addr_list, protocol):
        super().__init__(components, protocol)
        print("Init TMF882x Sensor Set")
        self._tmf882xList = list()

        for component, i2c_addr in zip(self, i2c_addr_list):
            self._tmf882xList.append(TMF882xPico(component, i2c_addr))
