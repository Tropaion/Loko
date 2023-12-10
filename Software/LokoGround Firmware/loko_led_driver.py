# Import periphery drivers
from machine import Pin, PWM

# Import constants
from loko_constants import (
    PWM_FREQUENCY,
    MAX_DUTY_CYCLE,
    RGB_LED_RED_GPIO,
    RGB_LED_GREEN_GPIO,
    RGB_LED_BLUE_GPIO
    )

# Class to drive rgb led
# Signal levels are inverted
class loko_led_driver:
    def __init__(self):
        # Create pwm objects
        self.__ledRed = PWM(RGB_LED_RED_GPIO, freq = PWM_FREQUENCY, duty = MAX_DUTY_CYCLE)
        self.__ledGreen = PWM(RGB_LED_GREEN_GPIO, freq = PWM_FREQUENCY, duty = MAX_DUTY_CYCLE)
        self.__ledBlue = PWM(RGB_LED_BLUE_GPIO, freq = PWM_FREQUENCY, duty = MAX_DUTY_CYCLE)
        
        # Initialize pulse helper variable
        self.__pulse_incrementing = True
        self.__pulse_value = 0
    
    # Calculate duty cycle according to percentage (inverted signal)
    def _percentage_to_duty_cycle(self, percentage):
        if percentage >= 100:
            return 0
        elif percentage <= 0:
            return MAX_DUTY_CYCLE
        else:
            return round(MAX_DUTY_CYCLE/100 * (100 - percentage))
        
    # Set brighness of provided color
    def set_brightness(self, color, brightness):
        if color == "green":
            self.__ledGreen.duty(self._percentage_to_duty_cycle(brightness))
        elif color == "red":
            self.__ledRed.duty(self._percentage_to_duty_cycle(brightness))
        elif color == "blue":
            self.__ledBlue.duty(self._percentage_to_duty_cycle(brightness))

    # Simulate pulse step by step with each call
    # Used with timer
    def pulse_helper(self, color, max_percentage):
        # Check if to increment or decrement
        if self.__pulse_incrementing:
            # Increment value
            self.__pulse_value += 1
            # Check if peak was reached
            if self.__pulse_value >= max_percentage:
                self.__pulse_value = max_percentage
                self.__pulse_incrementing = False
        else:
            # Decrement value
            self.pulse_value -= 1
            # Check if low was reached
            if self.__pulse_value <= 1:
                self.__pulse_value = 1
                self.__pulse_incrementing = True
        
        # Update brightness
        self.set_brightness(color, self.__pulse_value)