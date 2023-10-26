from PicoControl.Com.PicoInput import PicoInput
from PicoControl.Com.PicoOutput import PicoOutput
from RoboControl.Com.Connection import Connection
from RoboControl.Com.RemoteDataPacket import RemoteDataPacket
import rp2
import utime
import _thread

Connection_Counter = 0
Thread_Active = False
Subroutine_List = []

class PicoConnection(Connection):
    connected: bool = False

    def __init__(self, meta_data):
        super().__init__()
        print("PicoConnection - init")
        self._rxpin = meta_data["rx_pin"]		#extract receiver pin from settings
        self._txpin = meta_data["tx_pin"]		#extract transmitter pin from settings
        self._clock_pin = meta_data["clock_pin"]#extract clock pin from settings
        
        # clear programs form pio for clean restart
        rp2.PIO(0).remove_program()
        rp2.PIO(1).remove_program()



    def connect(self, listener) -> None:
        global Subroutine_List
        global Connection_Counter
        global Thread_Active
        super().connect(listener)
        if not self.connected:
            self._data_output = PicoOutput(Connection_Counter, self._txpin, self._clock_pin) # add data_output
            self._data_input = PicoInput(Connection_Counter, self._rxpin, self._clock_pin) # add data_input
            Subroutine_List.append(self._data_output.process)
            Subroutine_List.append(self._data_input.process)
            print('Connection counter: ' + str(Connection_Counter))
            Connection_Counter += 2
        
        if not Thread_Active:
            _thread.start_new_thread(self.connection_thread, ())
            Thread_Active = True
            
    def disconnect(self) -> None:
        self._data_input.stop()
        self._data_output.stop()
        super().disconnect()


        
    def connection_thread(self):
        while True:
            for subroutine in Subroutine_List:
                subroutine()


