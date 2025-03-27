import time
import pandas as pd
import paho.mqtt.client as mqtt
import threading

THINGSBOARD_HOST = "demo.thingsboard.io"
THINGSBOARD_ACCESS_TOKEN = "aYjzIENDYsDlM0hreMl7"  # Replace with your actual token
THINGSBOARD_TOPIC = "v1/devices/me/telemetry"

MOSQUITTO_HOST = "localhost"
MOSQUITTO_PORT = 1883
MOSQUITTO_TOPIC = "sensor/temperature"
MOSQUITTO_ALERT_TOPIC = "sensor/alerts"  # Listening topic

lock=threading.Lock()

data = pd.read_csv('/home/coder/project/Ubiquitous/Crop_recommendationV2.csv')
temperature_data = data['temperature'].to_list()

thingsboard_client = mqtt.Client()
thingsboard_client.username_pw_set(THINGSBOARD_ACCESS_TOKEN)
thingsboard_client.connect(THINGSBOARD_HOST, 1883, 60)

mosquitto_client = mqtt.Client()
mosquitto_client.connect(MOSQUITTO_HOST, MOSQUITTO_PORT, 60)

def on_message(client, userdata, msg):
    print(f"\n🔔 [Received] Topic: {msg.topic} | Message: {msg.payload.decode()}\n")
    with lock:
        for x in range(10):
            print(x+1)
            time.sleep(1)

mosquitto_client.on_message = on_message
mosquitto_client.subscribe(MOSQUITTO_ALERT_TOPIC)

mosquitto_client.loop_start()

while True:
    for temperature in temperature_data:
        with lock:
            print(f"[ThingsBoard] Publishing Temperature: {temperature}")
            thingsboard_client.publish(THINGSBOARD_TOPIC, f'{{"temperature": {temperature}}}')
            print(f"[Mosquitto] Publishing Temperature: {temperature}")
            mosquitto_client.publish(MOSQUITTO_TOPIC, f'{{"temperature": {temperature}}}')
            time.sleep(5)  # Send data every 5 seconds
