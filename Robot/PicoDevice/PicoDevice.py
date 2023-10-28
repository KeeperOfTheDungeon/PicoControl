
from RoboControl.Robot.AbstractRobot.AbstractRobotDevice import AbstractRobotDevice
from RoboControl.Robot.Device.RobotDevice import RobotDevice
class PicoDevice(RobotDevice):

    def __init__(self, component_config):
        super().__init__(component_config)
        self._connected_to_maiun_hub = False
       # self.build()

    def is_connected(self):
        return(self._connected_to_maiun_hub)

    def send_data(self, data: RemoteData) -> bool:
        # print("ARD: send Data", data_packet)
        #data.set_source_address(self.get_id())
        data.set_source_address(self._id)
        data.set_destination_address(0)
        print("send : ",str(data))
        if self._transmitter is None:
            return False
        return self._transmitter.transmitt(data)

    def process_ping_response(self,  Msg_pingResponse):
        print("got ping22")
        
        if Msg_pingResponse.get_source_address() == 0:
            self._connected_to_maiun_hub = True
            print("connected_to_maiun_hub")
  
