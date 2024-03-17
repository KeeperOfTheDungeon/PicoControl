#import traceback
#from typing import TypeAlias

#from serial import Serial
from machine import Pin
#from time import sleep
import rp2

from RoboControl.Com.RemoteDataPacket import RemoteDataPacket
from RoboControl.Com.RemoteData import RemoteData
from RoboControl.Com.Connection import RemoteDataOutput
from PicoControl.com.DataPacketPico import DataPacketPico
from RoboControl.Com.RemoteData import RemoteCommandDataPacket, RemoteMessageDataPacket, RemoteStreamDataPacket


class PicoOutput(RemoteDataOutput):

    def __init__(self, connection_counter, txpin, clock_pin):
        tx = tx_factory(clock_pin)
        self._state_machine_tx = rp2.StateMachine(connection_counter + 1, tx, freq=1000000, out_base=Pin(txpin), sideset_base=Pin(txpin))
        self._state_machine_tx.active(1)

    def transmitt(self, data_packet: RemoteDataPacket) -> None:
        print("PO : transmit ")
        print(str(RemoteDataPacket))
        pico_data = DataPacketPico()
        pico_data.code(data_packet)
        token_buffer = pico_data.get_buffer()
    
        self._state_machine_tx.put(pico_data.get_sync_token()) # write sync
    
        for token in token_buffer:
            self._state_machine_tx.put(token)
       
        self._state_machine_tx.put(pico_data.get_end_token())		# write end

        print("PO : transmit done",data_packet)

    def stop(self):
        self._state_machine_tx.active(0)
        
        
    def process(self):
        pass
        
        
def tx_factory(clock_pin):
    @rp2.asm_pio(out_init=rp2.PIO.OUT_HIGH,
             out_shiftdir=rp2.PIO.SHIFT_RIGHT,
             sideset_init=rp2.PIO.OUT_HIGH)
    def tx():
        wrap_target()

        #start bit
        pull()
        wait(0, gpio, clock_pin)
        set(x, 8)    .side(0)
        wait(1, gpio, clock_pin)

        # message
        label('loop')
        wait(0, gpio, clock_pin)
        out(pins, 1)
        wait(1, gpio, clock_pin)
        jmp(x_dec, 'loop')

        #end bit
        wait(0, gpio, clock_pin)
        nop()    .side(1)
        wait(1, gpio, clock_pin)
        
        
        wait(0, gpio, clock_pin)
        nop()    .side(1)
        wait(1, gpio, clock_pin)

        wrap()
    return tx



