import time
import RPi.GPIO as GPIO
import Adafruit_DHT
from hx711 import HX711
import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_BROKER = "mqtt.eclipse.org"  # Replace with actual broker
MQTT_TOPIC = "iot/pill_dispenser"
MQTT_CLIENT_ID = "pill_dispenser_client"

# GPIO Setup for height sensor (Ultrasonic) and Servo
GPIO.setmode(GPIO.BCM)

# DHT22 Sensor (Temperature and Humidity)
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4  # GPIO pin where the DHT22 is connected

# Ultrasonic Sensor for lid status (Height sensor)
TRIG_PIN = 17
ECHO_PIN = 27

# Servo Motor (connected to GPIO pin 18)
SERVO_PIN = 18

# Load Cell for weight sensing
hx = HX711(dout_pin=5, pd_sck_pin=6)

# MQTT Client Setup
client = mqtt.Client(MQTT_CLIENT_ID)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    message = msg.payload.decode("utf-8")
    print(f"Received message: {message}")
    if message == "SET_ALARM":
        trigger_dispense()  # Call to trigger the dispensing of the pill
    elif message == "CANCEL_ALARM":
        stop_dispense()  # Stop the dispensing process

client.on_connect = on_connect
client.on_message = on_message

def start_mqtt():
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_start()

def stop_mqtt():
    client.loop_stop()
    client.disconnect()

# Get temperature and humidity from DHT22 sensor
def get_temperature_humidity():
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        return round(temperature, 1), round(humidity, 1)
    else:
        return None, None

# Get the status of the lid (height sensor using ultrasonic)
def get_lid_status():
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    
    GPIO.output(TRIG_PIN, False)
    time.sleep(2)
    
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)
    
    pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
    
    pulse_end = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Speed of sound (34300 cm/s) divided by 2
    distance = round(distance, 2)
    
    # Lid open if distance is small (assuming small distance when lid is close)
    if distance < 10:  # Customize this threshold
        return "Closed"
    else:
        return "Open"

# Get weight from load cell
def get_weight():
    try:
        hx.power_up()
        time.sleep(0.1)
        weight = hx.get_weight_mean(5)
        hx.power_down()
        return round(weight, 2)
    except Exception as e:
        print("Error reading weight:", e)
        return None

# Trigger pill dispense (servo motor control)
def trigger_dispense():
    # Control the servo to dispense the pill
    print("Dispensing pill...")
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    pwm = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz pulse frequency
    pwm.start(0)
    pwm.ChangeDutyCycle(7)  # Move servo to dispense position (Adjust as needed)
    time.sleep(1)  # Allow time for servo to move
    pwm.ChangeDutyCycle(0)  # Stop servo
    pwm.stop()

def stop_dispense():
    print("Pill dispense stopped.")

# Get status data for updating UI
def get_status():
    temperature, humidity = get_temperature_humidity()
    lid_status = get_lid_status()
    weight = get_weight()
    
    return {
        "temperature": temperature if temperature is not None else "N/A",
        "humidity": humidity if humidity is not None else "N/A",
        "lid_status": lid_status,
        "weight": weight if weight is not None else "N/A"
    }
