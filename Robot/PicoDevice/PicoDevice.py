from RoboControl.Com import RemoteData
from RoboControl.Robot.AbstractRobot.AbstractRobotDevice import AbstractRobotDevice
from RoboControl.Robot.Device.RobotDevice import RobotDevice


class PicoDevice(RobotDevice):

    def __init__(self, device_meta_data):
        super().__init__(device_meta_data)
        self._connected_to_main_hub = False

    def is_connected(self):
        return(self._connected_to_main_hub)

    def send_data(self, data: RemoteData) -> bool:
        data.set_source_address(self._id)
        data.set_destination_address(0)
        print("send : ", str(data))
        if self._transmitter is None:
            return False
        return self._transmitter.transmitt(data)

    def process_ping_response(self, Msg_pingResponse):
        print("Received ping")
        
        if Msg_pingResponse.get_source_address() == 0:
            self._connected_to_main_hub = True
            print("connected_to_main_hub")
  
