from PicoControl.com.tmf8821.com.i2c_com import I2C_com
from PicoControl.com.tmf8821.tmf8821_app import Tmf8821App, TMF8821ResultFrame
from PicoControl.com.tmf8821.tmf8821_utility import Tmf8821Utility
from RoboControl.Robot.Component.Sensor.TMF882x import TMF882xSet, TMF882x
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

        #soft_timer = Timer(mode=Timer.PERIODIC, period=1000, callback=self.measure)

    def measure(self, timer):
        frame = self.tof.measure_frame()
        if frame is not None and len(frame) > 0:

            frame[0].print()


class TMF882xPicoSet(TMF882xSet):

    def __init__(self, components, i2c_addr_list, protocol):
        super().__init__(components, protocol)
        print("Init TMF882x Sensor Set")
        self._tmf882xList = list()

        for component, i2c_addr in zip(self, i2c_addr_list):
            self._tmf882xList.append(TMF882xPico(component, i2c_addr))
