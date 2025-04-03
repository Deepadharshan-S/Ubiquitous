import time
import pandas as pd
import paho.mqtt.client as mqtt
import json
import random
import threading
import os

THINGSBOARD_HOST = "demo.thingsboard.io"
THINGSBOARD_ACCESS_TOKEN = "q6qfq9v40tbzybzlzo6p"
THINGSBOARD_TOPIC = "v1/devices/me/telemetry"

MOSQUITTO_HOST = "localhost"
MOSQUITTO_PORT = 1883
MOSQUITTO_TOPIC = "sensor/readings"
MOSQUITTO_ALERT_TOPIC = "sensor/alerts"
MOSQUITTO_ACK_TOPIC = "sensor/ack"  # New topic for acknowledgment

HUMIDIFIER_FLAG = True
flag_lock = threading.Lock()

try:
    data = pd.read_csv('/home/deepadharshan/Downloads/Ubiquitous/Crop_recommendationV2.csv')
    humidity_data = data['humidity'].to_list()
except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit(1)

try:
    thingsboard_client = mqtt.Client()
    thingsboard_client.username_pw_set(THINGSBOARD_ACCESS_TOKEN)
    thingsboard_client.connect(THINGSBOARD_HOST, 1883, 60)

    mosquitto_client = mqtt.Client()
    mosquitto_client.on_message = None
    mosquitto_client.connect(MOSQUITTO_HOST, MOSQUITTO_PORT, 60)
except Exception as e:
    print(f"MQTT Connection Error: {e}")
    exit(1)

def send_gradual_humidity():
    min_humidity = float(os.getenv("HUMIDITY_THRESHOLD", 50))  
    humidity = min_humidity  

    while not HUMIDIFIER_FLAG:
        humidity = min(100, humidity + round(random.uniform(0.5, 1.5), 2))  
        payload = json.dumps({"humidity": humidity})

        print(f"[Mosquitto] Publishing Humidity Data: {payload}")
        mosquitto_client.publish(MOSQUITTO_TOPIC, payload)
        thingsboard_client.publish(THINGSBOARD_TOPIC, payload)
        
        time.sleep(2)  

def on_message(client, userdata, msg):
    global HUMIDIFIER_FLAG
    try:
        message = msg.payload.decode().strip()
        print(f"\n[Received] Topic: {msg.topic} | Message: {message}")

        with flag_lock:
            if message == "TURNING HUMIDIFIER ON":
                HUMIDIFIER_FLAG = False
                print("HUMIDIFIER activated. Sending acknowledgment.")
                mosquitto_client.publish(MOSQUITTO_ACK_TOPIC, "HUMIDIFIER ACKNOWLEDGED")

                threading.Thread(target=send_gradual_humidity, daemon=True).start()

            elif message == "TURNING HUMIDIFIER OFF":
                HUMIDIFIER_FLAG = True
                print("HUMIDIFIER deactivated. Resuming normal operation.")

    except Exception as e:
        print(f"Error in on_message: {e}")

mosquitto_client.on_message = on_message
mosquitto_client.subscribe(MOSQUITTO_ALERT_TOPIC)

try:
    mosquitto_client.loop_start()

    while True:
        for sample in humidity_data:
            while True:
                with flag_lock:
                    if HUMIDIFIER_FLAG:
                        break
                print("HUMIDIFIER is active...")
                time.sleep(2)
            
            try:
                payload = json.dumps({"humidity": sample})
                print(f"[ThingsBoard] Publishing: {payload}")
                thingsboard_client.publish(THINGSBOARD_TOPIC, payload)
                
                print(f"[Mosquitto] Publishing: {payload}")
                mosquitto_client.publish(MOSQUITTO_TOPIC, payload)
                
                time.sleep(2)
            except Exception as e:
                print(f"Error publishing MQTT message: {e}")

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    mosquitto_client.loop_stop()
    mosquitto_client.disconnect()
    thingsboard_client.disconnect()
    print("MQTT Clients Disconnected. Exiting.")
