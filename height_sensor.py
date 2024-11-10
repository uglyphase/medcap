import RPi.GPIO as GPIO
import time

# Pin setup
TRIG_PIN = 23  # Trigger pin
ECHO_PIN = 24  # Echo pin

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Function to measure distance
def measure_distance():
    # Send a trigger pulse
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    # Measure the time for the echo
    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        stop_time = time.time()

    # Calculate distance
    distance = ((stop_time - start_time) * 34300) / 2
    return distance

try:
    while True:
        print(f"Distance: {measure_distance():.2f} cm")
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
