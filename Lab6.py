from datetime import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import config
import json
import time
import ADC0832
import math

# Initialize the ADC0832
def init_sensor():
    ADC0832.setup()

# Function to read temperature from the sensor
def read_temperature():
    res = ADC0832.getADC(0)
    Vr = 3.3 * float(res) / 255
    Rt = 10000 * Vr / (3.3 - Vr)
    temp_kelvin = 1 / (((math.log(Rt / 10000)) / 3950) + (1 / (273.15 + 25)))
    temp_celsius = temp_kelvin - 273.15
    temp_fahrenheit = temp_celsius * 1.8 + 32
    return temp_celsius, temp_fahrenheit

# User specified callback function
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

# Configure the MQTT client
myMQTTClient = AWSIoTMQTTClient(config.CLIENT_ID)
myMQTTClient.configureEndpoint(config.AWS_HOST, config.AWS_PORT)
myMQTTClient.configureCredentials(config.AWS_ROOT_CA, config.AWS_PRIVATE_KEY, config.AWS_CLIENT_CERT)
myMQTTClient.configureConnectDisconnectTimeout(config.CONN_DISCONN_TIMEOUT)
myMQTTClient.configureMQTTOperationTimeout(config.MQTT_OPER_TIMEOUT)

# Connect to MQTT Host
if myMQTTClient.connect():
    print('AWS connection succeeded')

# topic
myMQTTClient.subscribe(config.TOPIC, 1, customCallback)
time.sleep(2)

#  sensor
init_sensor()

try:
    start_time = time.time() 
    device_id = 22  # change
    while time.time() - start_time < 120:  # 2 min
        temperature_c, temperature_f = read_temperature()
        payload = json.dumps({
            "device_id": device_id,
            "temperature_celcius": temperature_c,
            "temperature_Fahrenheit": temperature_f
        })
        myMQTTClient.publish(config.TOPIC, payload, 1)
        print(f"Sent: {payload} to {config.TOPIC}")
        time.sleep(5)
except KeyboardInterrupt:
    ADC0832.destroy()
    print('The end!')
