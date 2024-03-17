from RoboControl.Robot.Component.Actor.Servo import Servo, ServoSet
from RoboControl.Robot.Component.Actor.ServoProtocol import Cmd_servoOn, Cmd_servoOff, Msg_servoPosition, Msg_servoSpeed, Msg_servoStatus
from RoboControl.Robot.Device.RemoteProcessor import RemoteProcessor
from machine import Pin, PWM, Timer
import ujson

SERVO_WORK_PERIOD = 2000 # TMP from C
SERVO_DEFAULT_STEP_SIZE = 20 # TMP from C

class ServoPico:
    def __init__(self, servo: Servo, pin):
        self._servo = servo
        self._pwm_pin = PWM(Pin(pin))
        self._pwm_duty_value = 0
        self._scale = 17000 # from C
        self._inverted = False
        self._calibrated = False
        self._calibrate_direction = 0
        self.is_calibrating = False
        
        self.load_servo_defaults()
        
    def _update_pwm(self):
        self._pwm_pin.duty_u16(self._pwm_duty_value)
    
    # Clamp destination to servo range
    def _clamp_destination(self, destination):
        if destination > self._servo.get_max_range():
            destination = self._servo.get_max_range()
        elif destination < self._servo.get_min_range():
            destination = self._servo.get_min_range()
        return destination
    
    def get_local_id(self):
        return self._servo.get_local_id()
    
    def send_data(self, data):
        return self._servo.send_data(data)
    
    def servo_on(self):
        self._servo.set_on(True)
        self._pwm_pin.freq(50)
        self._pwm_pin.duty_ns(0)
        
    def servo_off(self):
        self._servo.set_on(False)
        self._pwm_pin.deinit()

    def get_position(self):
        return self._servo.get_position()
        
    def set_position(self, position):
        self._servo.set_position(position)
        self._servo.set_destination(position)
    
    def get_destination(self):
        return self._servo.get_destination()
    
    def set_destination(self, destination):
        self._servo.set_destination(destination)
    
    def move_to(self, destination):
        destination = self._clamp_destination(destination)
        self.set_speed(SERVO_DEFAULT_STEP_SIZE)
        self.set_destination(destination)

    def move(self, speed):
        if speed == 0:
            self.set_destination(self.get_position())
            self.set_speed(0)
        elif speed > 0:
            max_range = self._servo.get_destination_value().get_max_range()
            self.set_destination(max_range)
            self._step_size = speed
        else:
            min_range = self._servo.get_destination_value().get_min_range()
            self.set_destination(min_range)
            self.set_speed(speed)

    def move_to_at_speed(self, destination, speed):
        destination = self._clamp_destination(destination)
        self.set_destination(destination)
        self.set_speed(speed)

    def get_speed(self):
        return self._servo.get_speed()

    def set_speed(self, velocity):
        self._servo.set_speed(velocity)

    def get_servo_settings(self):
        pass

    def set_servo_settings(self):
        pass

    def load_servo_defaults(self):
        with open("Config/servo_defaults.json", "r") as f:
            all_defaults = ujson.load(f)
        try:
            defaults = all_defaults[str(self.get_local_id())]
        except KeyError:
            # This servo has no saved defaults
            return
        self._servo.set_on(defaults["is_on"])
        self._servo.set_active(defaults["active"])
        self._inverted = defaults["inverted"]
        self._servo.set_at_min(defaults["is_at_min"])
        self._servo.set_at_max(defaults["is_at_max"])
        self._servo.set_stalling(defaults["is_stalling"])
        self._servo.set_force_feedback_on(defaults["force_feedback"])
        self._servo.set_position_feedback_on(defaults["position_feedback"])
        self._calibrated = defaults["calibrated"]
        self._calibrate_direction = defaults["calibrate_direction"]
        self.is_calibrating = defaults["is_calibrating"]
        self._servo.set_min_range(defaults["min_range"])
        self._servo.set_max_range(defaults["max_range"])
        self._servo.set_speed(defaults["speed"])
        self._servo.set_offset(defaults["offset"])
        self._scale = defaults["scale"]
        print(f"Loaded defaults for servo with id {self.get_local_id()}")

    def save_servo_defaults(self):
        defaults = {
            "is_on": self._servo.is_on(),
            "active": self._servo.is_active(),
            "inverted": self._inverted,
            "is_at_min": self._servo.is_at_min(),
            "is_at_max": self._servo.is_at_max(),
            "is_stalling": self._servo.is_stalling(),
            "force_feedback": self._servo.is_force_feedback_on(),
            "position_feedback": self._servo.is_position_feedback_on(),
            "calibrated": self._calibrated,
            "calibrate_direction": self._calibrate_direction,
            "is_calibrating": self.is_calibrating,
            "min_range": self._servo.get_min_range(),
            "max_range": self._servo.get_max_range(),
            "speed": self._servo.get_speed(),
            "offset": self._servo.get_offset(),
            "scale": self._scale
        }
        with open("Config/servo_defaults.json", "r") as f:
            try:
                all_defaults = ujson.load(f)
            except ValueError:
                # File is empty
                all_defaults = {}
        all_defaults[self.get_local_id()] = defaults
        print(len(all_defaults))
        with open("Config/servo_defaults.json", "w") as f:
            ujson.dump(all_defaults, f)
        print(f"Saved defaults for servo with id {self.get_local_id()}")

class ServoSetPico(ServoSet):
    def __init__(self, components, pin_list, protocol):
        super().__init__(components, protocol)
        self._servoList = list()
        self.counter = 0

        for component, pin in zip(self, pin_list):
            self._servoList.append(ServoPico(component, pin))
            
        self._move_cycle_timer = Timer(mode=Timer.PERIODIC, period=10, callback=self.position_move_cycle_handler)
        
        
    def _get_servo(self, index) ->  ServoPico: # type: ignore
        for servo in self._servoList:
            if servo.get_local_id() == index:
                return servo
    
    def save_defaults(self, index):
        servo = self._get_servo(index)
        if not servo:
            return False
        servo.save_servo_defaults()

    def load_defaults(self, index):
        servo = self._get_servo(index)
        if not servo:
            return False
        servo.load_servo_defaults()

    def remote_get_position_response(self, index):
        servo = self._get_servo(index)
        if not servo:
            return False
        msg = Msg_servoPosition.get_command(self._msg_servo_position, servo.get_local_id(), servo.get_position())
        return servo.send_data(msg)
    
    def remote_get_speed_response(self, index):
        servo = self._get_servo(index)
        if not servo:
            return False
        msg = Msg_servoSpeed.get_command(self._msg_servo_speed, servo.get_local_id(), servo.get_speed())
        return servo.send_data(msg)
    
    def remote_get_status_response(self, index):
        servo = self._get_servo(index)
        if not servo:
            return False
        msg = Msg_servoStatus.get_command(
            self._msg_servo_status,
            servo.get_local_id(),
            servo._servo.is_on(),
            servo._servo.is_active(),
            servo._servo.is_reverse(),
            servo._servo.is_at_min(),
            servo._servo.is_at_max(),
            servo._servo.is_stalling()
        )
        return servo.send_data(msg)

    def set_position(self, index, position):
        self._get_servo(index).set_position(position)
        
    def servo_on(self, index):
        servo = self._get_servo(index)
        if not servo:
            return False
        servo.servo_on()
        
    def servo_off(self, index):
        servo = self._get_servo(index)
        if not servo:
            return False
        servo.servo_off()
        
    def move(self, index, velocity):
        servo = self._get_servo(index)
        if not servo:
            return False
        servo.move(velocity)

    def move_to(self, index, destination):
        servo = self._get_servo(index)
        if not servo:
            return False
        servo.move_to(destination)

    def move_to_at_speed(self, index, destination, speed):
        servo = self._get_servo(index)
        if not servo:
            return False
        servo.move_to_at_speed(destination, speed)
        
    def _setup_test(self):
        Timer(mode=Timer.ONE_SHOT, period=6000, callback=self._tester_on)
        Timer(mode=Timer.ONE_SHOT, period=8000, callback=self._tester_left)
        Timer(mode=Timer.ONE_SHOT, period=12000, callback=self._tester_right)
        
    def _tester_on(self, timer):
        servo = self._get_servo(1)
        servo.servo_on()
    
    def _tester_left(self, timer):
        print("TESTING LEFT")
        servo = self._get_servo(1)
        servo.set_speed(50)
        servo.set_destination(-20000.0)
        
    def _tester_right(self, timer):
        print("TESTING RIGHT")
        servo = self._get_servo(1)
        servo.set_speed(50)
        servo.set_destination(28000.0)
    
    # WIP
    def position_move_cycle_handler(self, timer):
        for servo_pico in self._servoList:
            servo = servo_pico._servo
            if not servo.is_on():
                continue
            
            # Moving in negative direction
            if servo.get_position() > servo.get_destination():
                position = servo.get_position() - servo.get_speed()

                # Next step would overshoot, so set position to destination
                if position < servo.get_destination():
                    position = servo.get_destination()

                servo.set_active(True)
            # Moving in positive direction
            elif servo.get_position() < servo.get_destination():
                position = servo.get_position() + servo.get_speed()

                # Next step would overshoot, so set position to destination
                if position > servo.get_destination():
                    position = servo.get_destination()
                servo.set_active(True)
            else:
                servo.set_active(False)
                position = servo.get_position()

            if position >= servo.get_max_range():
                servo.set_at_max(True)
                position = servo.get_max_range()
            else:
                servo.set_at_max(False)

            if position <= servo.get_min_range():
                servo.set_at_min(True)
                position = servo.get_min_range()
            else:
                servo.set_at_min(False)

            servo.set_position(position)
            
            tmp_value = SERVO_WORK_PERIOD
            tmp_value *= servo.get_position()
            tmp_value /= servo_pico._scale

            if servo_pico._inverted:
                servo_pico._pwm_duty_value = int(servo.get_offset() - tmp_value)
            else:
                servo_pico._pwm_duty_value = int(servo.get_offset() + tmp_value)
            
            if self.counter % 100 == 0:
                print(f"Servo {servo.get_local_id()} moving from {servo.get_position()} to {servo.get_destination()} at speed {servo.get_speed()} with pwm {servo_pico._pwm_duty_value}")
            self.counter += 1
            if servo.is_on():
                servo_pico._update_pwm()

