from PicoControl.Com.tmf8821.com.i2c_com import I2C_com
from PicoControl.Com.tmf8821.tmf8821_app import Tmf8821App, TMF8821ResultFrame, TMF8821MeasureResult
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

        self.tof.log("Try to open connection")
        if Tmf8821App.Status.OK != self.tof.open():
            self.tof.error("Error open FTDI device")
            raise RuntimeError("Error open FTDI device")
        else:
            self.tof.log("Opened connection")

        self.tof.init_bootloader_check()

    def measure(self):
        frame = self.tof.measure_frame()
        if frame is not None and len(frame) > 0:
            header = frame[0]
            results = header.results
            sensors = self._sensor.get_distance_sensors()
            self.tof.log("Number of Sensors: {}".format(len(sensors)))
            self.tof.log("Number of Results: {}".format(len(results)))

            for i in range(0, (len(results) % len(sensors))):
                sensor = sensors[i]
                if isinstance(sensor, TMF882xDistanceSensor):
                    result = results[i]

                    if isinstance(result, TMF8821MeasureResult):
                        print("---- Distance in Sensor ---- ", result.print())
                        sensor.set_distance(result.distanceInMm)
                        sensor.set_confidence(result.confidence)
                        sensor.remote_msg_distance()
                else:
                    self.tof.error("Sensor Type Error")


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
            self._tmf882xList[index - 1].measure()
