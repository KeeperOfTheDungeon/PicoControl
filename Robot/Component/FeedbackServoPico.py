from PicoControl.Robot.Component.ServoPico import ServoPico, ServoSetPico
from RoboControl.Robot.Component.Actor.FeedbackServo import FeedbackServo
from machine import Timer, Pin, ADC
from time import sleep

SERVO_WORK_PERIOD = 2000 # TMP from C
SERVO_DEFAULT_STEP_SIZE = 20 # TMP from C

class FeedbackServoPico(ServoPico):
    def __init__(self, servo: FeedbackServo, pwm_pin, position_adc_pin, force_adc_pin) -> None:
        super().__init__(servo, pwm_pin)
        self._position_adc = ADC(Pin(position_adc_pin))
        self._position_adc_min = 0
        self._position_adc_max = 0
        self._force_adc = ADC(Pin(force_adc_pin))
        self._force_adc_value = 0
        self._calibration_counter = 0

    def _read_force(self):
        self._force_adc_value = self._force_adc.read_u16()

    def set_postion_feedback_on(self):
        self._servo.set_position_feedback_on(True)

    def set_postion_feedback_off(self):
        self._servo.set_position_feedback_on(False)

    def set_force_feedback_on(self):
        self._servo.set_force_feedback_on(True)
    
    def set_force_feedback_off(self):
        self._servo.set_force_feedback_on(False)
        

class FeedbackServoSetPico(ServoSetPico):
    def __init__(self, components, pwm_pin_list, position_adc_pin_list, force_adc_pin_list, protocol):
        super().__init__(components, pwm_pin_list, protocol)
        self._servoList = list()
        self.counter = 0

        for component, pwm_pin, position_adc_pin, force_adc_pin in zip(self, pwm_pin_list, position_adc_pin_list, force_adc_pin_list):
            self._servoList.append(FeedbackServoPico(component, pwm_pin, position_adc_pin, force_adc_pin))
            
        self._move_cycle_timer = Timer(mode=Timer.PERIODIC, period=10, callback=self.position_move_cycle_handler)


    def _get_servo(self, index) ->  FeedbackServoPico: # type: ignore
        for servo in self._servoList:
            if servo.get_local_id() == index:
                return servo
    
    def _calibrate(self, index):
        servo = self._get_servo(index)
        if servo._calibrate_direction == 0:
            servo.move(50)
            servo.servo_on()
            if servo._calibration_counter > 500:
                servo._position_adc_max = servo._position_adc.read_u16()
                servo._calibrate_direction = 1
                servo._calibration_counter = 0
           
        else:
            servo.move(-50)
            servo.servo_on()
            if servo._calibration_counter > 500:
                servo._position_adc_min = servo._position_adc.read_u16()
                servo._calibrate_direction = 0
                servo._calibration_counter = 0
                servo._calibrated = True
                servo.servo_off()
                print(f"Calibrated servo {index} with min {servo._position_adc_min} and max {servo._position_adc_max}")

        servo._calibration_counter += 1

        
    def position_move_cycle_handler(self, timer):
        for feedback_servo_pico in self._servoList:
            feedback_servo = feedback_servo_pico._servo

            if feedback_servo.is_calibrating():
                self._calibrate(feedback_servo.get_local_id())

            if not feedback_servo.is_on():
                continue

            if feedback_servo.is_force_feedback_on():
                feedback_servo_pico._read_force()
                if feedback_servo.get_force_threshold() < feedback_servo_pico._force_adc_value:
                    feedback_servo.set_destination(feedback_servo.get_position())
                    feedback_servo.set_stalling(True)
                    continue
                
            
            # Moving in negative direction
            if feedback_servo.get_position() > feedback_servo.get_destination():
                position = feedback_servo.get_position() - feedback_servo.get_speed()

                # Next step would overshoot, so set position to destination
                if position < feedback_servo.get_destination():
                    position = feedback_servo.get_destination()

                feedback_servo.set_active(True)
            # Moving in positive direction
            elif feedback_servo.get_position() < feedback_servo.get_destination():
                position = feedback_servo.get_position() + feedback_servo.get_speed()

                # Next step would overshoot, so set position to destination
                if position > feedback_servo.get_destination():
                    position = feedback_servo.get_destination()
                feedback_servo.set_active(True)
            else:
                feedback_servo.set_active(False)
                position = feedback_servo.get_position()

            if position >= feedback_servo.get_max_range():
                feedback_servo.set_at_max(True)
                position = feedback_servo.get_max_range()
            else:
                feedback_servo.set_at_max(False)

            if position <= feedback_servo.get_min_range():
                feedback_servo.set_at_min(True)
                position = feedback_servo.get_min_range()
            else:
                feedback_servo.set_at_min(False)

            feedback_servo.set_position(position)
            
            tmp_value = SERVO_WORK_PERIOD
            tmp_value *= feedback_servo.get_position()
            tmp_value /= feedback_servo_pico._scale

            if feedback_servo_pico._inverted:
                feedback_servo_pico._pwm_duty_value = int(feedback_servo.get_offset() - tmp_value)
            else:
                feedback_servo_pico._pwm_duty_value = int(feedback_servo.get_offset() + tmp_value)
            
            # Print status 1x per second
            if self.counter % 100 == 0:
                print(f"Servo {feedback_servo.get_local_id()} moving from {feedback_servo.get_position()} to {feedback_servo.get_destination()} at speed {feedback_servo.get_speed()} with pwm {feedback_servo_pico._pwm_duty_value}")
            self.counter += 1
            if feedback_servo.is_on():
                feedback_servo_pico._update_pwm()

