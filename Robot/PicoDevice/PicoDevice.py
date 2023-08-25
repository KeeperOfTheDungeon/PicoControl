from RoboControl.Robot.AbstractRobot.AbstractRobotDevice import AbstractRobotDevice
from RoboControl.Robot.Device.Protocol import DeviceProtocol
from RoboControl.Robot.Device.Protocol.Cmd_clearAllDataStreams import Cmd_clearAllDataStreams
from RoboControl.Robot.Device.Protocol.Cmd_clearComStatistics import Cmd_clearComStatistics
from RoboControl.Robot.Device.Protocol.Cmd_clearCpuStatistics import Cmd_clearCpuStatistics
from RoboControl.Robot.Device.Protocol.Cmd_continueAllDataStreams import Cmd_continueAllDataStreams
from RoboControl.Robot.Device.Protocol.Cmd_getNodeId import Cmd_getNodeId
from RoboControl.Robot.Device.Protocol.Cmd_loadDataStreams import Cmd_loadDataStreams
from RoboControl.Robot.Device.Protocol.Cmd_pauseAllDataStreams import Cmd_pauseAllDataStreams
from RoboControl.Robot.Device.Protocol.Cmd_ping import Cmd_ping
from RoboControl.Robot.Device.Protocol.Cmd_saveDataStreams import Cmd_saveDataStreams
from RoboControl.Robot.Device.Protocol.Cmd_startStreamData import Cmd_startStreamData
from RoboControl.Robot.Device.Protocol.Cmd_stopStreamData import Cmd_stopStreamData
from RoboControl.Robot.Device.Protocol.Msg_pingResponse import Msg_pingResponse
from RoboControl.Robot.Device.Protocol.Stream_comStatistics import Stream_comStatistics
from RoboControl.Robot.Device.Protocol.Stream_cpuStatistics import Stream_cpuStatistics
from RoboControl.Robot.Device.remoteProcessor.RemoteProcessor import RemoteProcessor


# from RoboControl.Com.Remote.RemoteCommand import RemoteCommand
# from RoboControl.Com.Remote.RemoteMessage import RemoteMessage


class PicoDevice(AbstractRobotDevice):

    def __init__(self, component_config):
        super().__init__(component_config)
       # self.build()

    # self.build_protocol()

    def get_data_aquisators(self):
        aquisators = ["cpu status", "com ststus"]
        return aquisators



    # remote commands

    def remote_ping_device(self):
        cmd = Cmd_ping.get_command(DeviceProtocol.CMD_PING)
        self.send_data(cmd)

    def remote_continue_streams(self):
        cmd = Cmd_continueAllDataStreams.get_command()
        self.send_data(cmd)

    def remote_pause_streams(self):
        cmd = Cmd_pauseAllDataStreams.get_command()
        self.send_data(cmd)

    def remote_clear_streams(self):
        cmd = Cmd_clearAllDataStreams.get_command()
        self.send_data(cmd)

    def remote_save_streams(self):
        cmd = Cmd_saveDataStreams.get_command()
        self.send_data(cmd)

    def remote_load_streams(self):
        cmd = Cmd_loadDataStreams.get_command()
        self.send_data(cmd)

    def remote_start_stream(self, index, period):
        cmd = Cmd_startStreamData.get_command(index, period)
        self.send_data(cmd)

    def remote_stop_stream(self, index):
        cmd = Cmd_stopStreamData.get_command(index)
        self.send_data(cmd)

    def remote_clear_cpu_statistics(self):
        cmd = Cmd_clearCpuStatistics.get_command()
        self.send_data(cmd)

    def Cmd_clear_com_statistics(self):
        cmd = Cmd_clearComStatistics.get_command()
        self.send_data(cmd)

    def process_ping_response(self, message_data):
        print("******************got ping response************************")

    def process_ping_command(self, command_data):
        msg = Msg_pingResponse.get_command(DeviceProtocol.MSG_PING_RESPONSE)
        self.send_data(msg)
        print("******************got ping command************************")

    def process_Node_id_command(self, command_data):
        print("******************got node Id command************************")

