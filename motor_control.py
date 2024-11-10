import RPi.GPIO as GPIO
import time

def activate_motor():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.OUT)
    pwm = GPIO.PWM(12, 50)
    pwm.start(7.5)
    
    # Rotate the motor
    pwm.ChangeDutyCycle(12.5)  # Adjust to rotate for dispensing
    time.sleep(1)
    
    pwm.ChangeDutyCycle(7.5)  # Return to starting position
    pwm.stop()
    GPIO.cleanup()
