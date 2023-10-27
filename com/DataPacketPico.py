from RoboControl.Com.RemoteData import RemoteData, RemoteCommand, RemoteMessage, RemoteStream
from RoboControl.Com.RemoteDataPacket import RemoteDataPacket

from time import sleep
from machine import Pin

# TODO "make enum"
COMMAND_START_TOKEN = 0x1FA

MESSAGE_START_TOKEN = 0x1FB

STREAM_START_TOKEN = 0x1FC

EXCEPTION_START_TOKEN = 0x1F3
ALLERT_START_TOKEN = 0x1F4

OK_START_TOKEN = 0x1FD
FAIL_START_TOKEN = 0x1FE
END_TOKEN = 0x1FF



#BUFFER_OFFSET_MESSAGE_TYPE = 0
BUFFER_OFFSET_DEST_ADDRESS = 0
BUFFER_OFFSET_SRC_ADDRESS = 1
BUFFER_OFFSET_ID = 2
BUFFER_OFFSET_PAYLOAD = 3


#DATA_PACKET_OFFSET_MESSAGE_TYPE = 0
#DATA_PACKET_OFFSET_DEST_ADDRESS = 1
#DATA_PACKET_OFFSET_SRC_ADDRESS = 2
#DATA_PACKET_OFFSET_ID = 3
#DATA_PACKET_OFFSET_PAYLOAD = 4

Byte: TypeAlias = int


class DataPacketPico(RemoteDataPacket):
    
    PACKET_RESYNC = 1
    PACKET_READY = 2
    TOKEN_FAILURE = 3
    
    # TODO why does this inherit from RemoteDataPacket without forwarding init
    def __init__(self):  # noqa


# Initialisierung von GPIO25 als Ausgang
        #self.led_onboard = Pin(25, Pin.OUT)
        self._token_counter = 0
        self._data_pointer = 0
        self._sync_type = 0
        self._data_buffer = bytearray(20)
        self._read = False
        
        pass

    def get_sync_token(self):
        return self._sync_type

    def get_end_token(self):
        return END_TOKEN

    def decode(self) -> RemoteData:
        
        message_type = self._sync_type | 0x100
        
        print(message_type)

        if message_type == COMMAND_START_TOKEN:
            print("Comand sync")
            remote_data = RemoteCommand(0, 0)
            self.do_decode(remote_data)
        elif message_type == MESSAGE_START_TOKEN:
            print("Message sync")
            remote_data = RemoteMessage(0, 0)
            self.do_decode(remote_data)
        elif message_type == STREAM_START_TOKEN:
            print("Stream sync")
            remote_data = RemoteStream(0, 0)
            self.do_decode(remote_data)
        else:
            print("unsync")
            remote_data = RemoteData(0, 0)

        return remote_data

    def do_decode(self, remote_data: RemoteData) -> None:
        remote_data._destination_address = int(self._data_buffer[BUFFER_OFFSET_DEST_ADDRESS])
        remote_data._source_address = int(self._data_buffer[BUFFER_OFFSET_SRC_ADDRESS])
        remote_data._id = int(self._data_buffer[BUFFER_OFFSET_ID])
        
        payload = bytearray(self._data_pointer-BUFFER_OFFSET_PAYLOAD) # TODO make with RemoteData class compatible
        
        from_index = BUFFER_OFFSET_PAYLOAD
        to_index = 0
        
        while (from_index) < (self._data_pointer):
            value = int(self._data_buffer[from_index])
            payload[to_index] = value
            from_index += 1
            to_index += 1

        remote_data.set_payload(payload)


    # TODO camelcase
    def putToken(self, token):  # noqa
        return_code = 0
  
        if token == END_TOKEN:
            self._read = True
            return_code = DataPacketPico.PACKET_READY

        elif (token & 0x200 == 0x200):
            self._data_pointer = 0
            return_code = DataPacketPico.TOKEN_FAILURE
      
        elif (token > 0xff ) and (token != END_TOKEN):
            self._data_pointer = 0
            self._sync_type = token & 0xff
            return_code = DataPacketPico.PACKET_RESYNC
        else:
            token &= 0xff
            self._data_buffer[self._data_pointer] = token
            self._data_pointer += 1

        return return_code


    def toggleRead(self):
        result = self._read
        self._read = False if result else self._read
        return result



    def code(self, data_packet: RemoteDataPacket):
        remote_data = data_packet.get_remote_data()
        frame_size = remote_data.get_payload_size()
        frame_size += BUFFER_OFFSET_PAYLOAD + 1 # one extra for the end byte

        self._data_buffer = [0 for x in range(frame_size)]

        # command mark
        if isinstance(remote_data, RemoteCommand):
            self._sync_type = COMMAND_START_TOKEN
        elif isinstance(remote_data, RemoteMessage):
            self._sync_type = MESSAGE_START_TOKEN

        self._data_buffer[BUFFER_OFFSET_DEST_ADDRESS] = remote_data.get_destination_address()
        self._data_buffer[BUFFER_OFFSET_SRC_ADDRESS] = remote_data.get_source_address()
        self._data_buffer[BUFFER_OFFSET_ID] = remote_data.get_id()
        # send Data payload

        self._data_buffer[len(self._data_buffer) - 1] = END_TOKEN
        index = BUFFER_OFFSET_PAYLOAD
        for parameter in remote_data.get_parameter_list():
            buffer = parameter.get_as_buffer()
            for byte in buffer:
                self._data_buffer[index] = byte
                index += 1

    def get_buffer(self):
        return self._data_buffer


