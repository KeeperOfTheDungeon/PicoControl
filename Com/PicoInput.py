from machine import Pin
import rp2

from RoboControl.Com.Connection import RemoteDataInput
from PicoControl.Com.DataPacketPico import DataPacketPico

class PicoInput(RemoteDataInput):
    def __init__(self, connection_counter, rxpin, clock_pin):
        self.led_onboard = Pin(5, Pin.OUT)
        Pin(rxpin, Pin.IN, Pin.PULL_UP)
        rx = rx_factory(clock_pin)
        self._state_machine_rx = rp2.StateMachine(connection_counter, rx, freq=10000000, in_base=Pin(rxpin), jmp_pin=Pin(rxpin))
        self._state_machine_rx.irq(self.interrupt_callback)
        self._data_packet = DataPacketPico()
        self._state_machine_rx.active(1)
        self.running = True

    def process(self):
        while self._state_machine_rx.rx_fifo() > 0:
                
            token = self._state_machine_rx.get()
                  
            if self._data_packet.putToken(token) == DataPacketPico.PACKET_READY:  # put token into datapacket - if endsync detected function will return True
                try:
                    remote_data = self._data_packet.decode()
                except MemoryError:
                    # Out of memory, dropping packet
                    print("Out of memory, dropped an incoming packet")
                    self._data_packet = DataPacketPico() # clear packet
                    continue
                
                data_packet = remote_data.get_data_packet()
                self.deliver_packet(data_packet)


    def stop(self):
        self.running = False
        self._state_machine_rx.active(0)

    def sync_error(self):
        print('sync error: usart did not recieve end bit')
        #ToDo abfangen und rücksetzen
        

    def interrupt_callback(self, x):
        print('Error in state machine. Interrupt thrown')

def rx_factory(clock_pin):
    @rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_RIGHT,
                fifo_join=rp2.PIO.JOIN_RX)
    def rx():
        wrap_target()

        # wait for start bit
        label('ready')
        wait(0, gpio, clock_pin)		# warte auf 0 bei clock
        wait(1, gpio, clock_pin)		# warte auf 1 bei clock
        jmp(pin, 'ready') 		# wenn pin High dann kein Startbit

        # accept message
        set(x, 8)				# setze counter auf 8 bits
        wait(0, gpio, clock_pin)
            
        label('loop')
            
        wait(1, gpio, clock_pin)
        in_(pins, 1)			# hole aktuelles bit
        wait(0, gpio, clock_pin)
            
        jmp(x_dec, 'loop')		# get next bit(as long as n > 0)

        # wait for end bit
        wait(1, gpio, clock_pin)
        jmp(pin, 'end_bit')

        # error as 10. LSB in word to main thread
        set(y, 1)
        in_(y, 23)
            
        jmp('end')				# ende

        # normal execution
        label('end_bit')	
        in_(null, 23)
            
        label('end')
        push()				# push data to RX FIFO

        wrap()
    return rx

class UARTInput(RemoteDataInput):
    def __init__(self, connection_counter, rxpin, baudrate=115200):
        self.led_onboard = Pin(5, Pin.OUT)
        rx_pin = Pin(rxpin, Pin.IN, Pin.PULL_UP)
        
        rx = uart_rx_factory(baudrate)
        self._state_machine_rx = rp2.StateMachine(
            connection_counter, 
            rx, 
            freq=10000000,
            in_base=rx_pin, 
            jmp_pin=rx_pin
        )

        self._state_machine_rx.irq(self.interrupt_callback)
        self._data_packet = DataPacketPico()
        self._state_machine_rx.active(1)
        self.running = True

    def process(self):
        while self._state_machine_rx.rx_fifo() > 0:
                
            token = self._state_machine_rx.get()
            print("Received byte:", token) 
            if self._data_packet.putToken(token) == DataPacketPico.PACKET_READY:
                try:
                    remote_data = self._data_packet.decode()
                except MemoryError:
                    # Out of memory, dropping packet
                    print("Out of memory, dropped an incoming packet")
                    self._data_packet = DataPacketPico() # clear packet
                    continue
                
                data_packet = remote_data.get_data_packet()
                self.deliver_packet(data_packet)

    def stop(self):
        self.running = False
        self._state_machine_rx.active(0)

    def sync_error(self):
        print('sync error: usart did not recieve end bit')
        #ToDo abfangen und rücksetzen
        

    def interrupt_callback(self, x):
        print('Error in state machine. Interrupt thrown')

def uart_rx_factory(baudrate=115200):
    bit_time = int(10000000 / baudrate)

    @rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_RIGHT,
                fifo_join=rp2.PIO.JOIN_RX)
    def rx():
        wrap_target()
        
        label("start_bit_wait")
        jmp(pin, "start_bit_wait")  # If pin is high, keep waiting
        
        # delay
        set(y, bit_time // 2)  # Half bit time
        label("start_bit_delay")
        jmp(y_dec, "start_bit_delay") [1]
        
        set(x, 8) # 8 bits
        
        label("bit_loop")
        
        # delay to read at middle
        set(y, bit_time)
        label("bit_delay")
        jmp(y_dec, "bit_delay") [1]
        
        
        in_(pins, 1) # sample
        
        jmp(x_dec, "bit_loop")
        
        # check stop
        set(y, bit_time)
        label("stop_bit_delay")
        jmp(y_dec, "stop_bit_delay") [1]
        
        # framing error
        jmp(pin, "valid_stop_bit")
        
        # Handle framing error
        set(y, 1)
        in_(y, 23)  # Shift into MSB of the output word
        jmp("finish")
        
        # everything okay
        label("valid_stop_bit")
        in_(null, 23)  # Add a 0 in error bit
        
        label("finish")
        push()
        
        wrap()
    
    return rx