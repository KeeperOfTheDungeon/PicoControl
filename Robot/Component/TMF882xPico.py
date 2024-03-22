from PicoControl.Com.tmf8821.com.i2c_com import I2C_com
from PicoControl.Com.tmf8821.tmf8821_app import Tmf8821App, TMF8821ResultFrame
from PicoControl.Com.tmf8821.tmf8821_utility import Tmf8821Utility
from RoboControl.Robot.Component.Sensor.DistanceSensorProtocol import Cmd_getDistance
from RoboControl.Robot.Component.Sensor.TMF882x import TMF882xSet, TMF882x, TMF882xDistanceSensor
from machine import Timer


class TMF882xPico:

    def __init__(self, sensor: TMF882x, i2c_addr):
        self._i2c_addr = i2c_addr
        self._sensor = sensor

        self.tof = Tmf8821Utility(
            ic_com=I2C_com()
        )

        self.tof._log("Try to open connection")
        if Tmf8821App.Status.OK != self.tof.open():
            self.tof._setError("Error open FTDI device")
            raise RuntimeError("Error open FTDI device")
        else:
            self.tof._log("Opened connection")

        self.tof.init_bootloader_check()

    def measure(self):
        frame = self.tof.measure_frame()
        if frame is not None and len(frame) > 0:
            counter = 0
            sensors = self._sensor.get_distance_sensors()

            print("number of sensors", len(sensors))
            print("numer of results", len(frame[0].results))
            frame[0].print()
            for sensor in sensors:
                if isinstance(sensor, TMF882xDistanceSensor):
                    print("---- Distance in Sensor ---- ", frame[0].results[counter])

                    sensor.set_distance(
                        frame[0].results[counter]
                        )
                    counter += 1
                    sensor.remote_msg_distance()
                else:
                    self.tof._setError("Sensor Type Error")


class TMF882xPicoSet(TMF882xSet):

    def __init__(self, components, i2c_addr_list, protocol):
        super().__init__(components, protocol)
        print("Init TMF882x Sensor Set")
        self._tmf882xList = list()

        for component, i2c_addr in zip(self, i2c_addr_list):
            self._tmf882xList.append(TMF882xPico(component, i2c_addr))

    def decode_command(self, remote_command):
        if isinstance(remote_command, Cmd_getDistance):
            cmd: Cmd_getDistance = remote_command
            index = cmd.get_parameter_list()[0].get_value()
            self._tmf882xList[index-1].measure()