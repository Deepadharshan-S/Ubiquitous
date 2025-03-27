import paho.mqtt.client as mqtt
import time
import threading

lock = threading.Lock()

MOSQUITTO_HOST = "localhost"
MOSQUITTO_PORT = 1883
MOSQUITTO_TOPIC = "sensor/temperature"

def on_message(client, userdata, msg):
    with lock:
        print(f"\n🔔 [Received] Topic: {msg.topic} | Message: {msg.payload.decode()}\n")

mosquitto_client = mqtt.Client()

mosquitto_client.on_message = on_message

mosquitto_client.connect(MOSQUITTO_HOST, MOSQUITTO_PORT, 60)

mosquitto_client.subscribe(MOSQUITTO_TOPIC)

mosquitto_client.loop_start()

print(f"Subscribed to {MOSQUITTO_TOPIC}. Waiting for messages...")

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting...")
finally:
    mosquitto_client.loop_stop()  # Stop the loop
    mosquitto_client.disconnect()  # Disconnect from the broker