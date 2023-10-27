
from RoboControl.Robot.AbstractRobot.AbstractRobotDevice import AbstractRobotDevice
from RoboControl.Robot.Device.RobotDevice import RobotDevice
class PicoDevice(RobotDevice):

    def __init__(self, component_config):
        super().__init__(component_config)
       # self.build()

    def send_data(self, data: RemoteData) -> bool:
        # print("ARD: send Data", data_packet)
        #data.set_source_address(self.get_id())
        data.set_source_address(22)
        data.set_destination_address(55)
        print("send : ",str(data))
        if self._transmitter is None:
            return False
        return self._transmitter.transmitt(data)


  
