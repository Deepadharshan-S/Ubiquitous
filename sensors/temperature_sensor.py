import time
import pandas as pd
import paho.mqtt.client as mqtt
import json
import random
import threading

THINGSBOARD_HOST = "demo.thingsboard.io"
THINGSBOARD_ACCESS_TOKEN = "aYjzIENDYsDlM0hreMl7"
THINGSBOARD_TOPIC = "v1/devices/me/telemetry"

MOSQUITTO_HOST = "localhost"
MOSQUITTO_PORT = 1883
MOSQUITTO_TOPIC = "sensor/readings"
MOSQUITTO_ALERT_TOPIC = "sensor/alerts"
MOSQUITTO_ACK_TOPIC = "sensor/ack"  # New topic for acknowledgment


FLAG = True
flag_lock = threading.Lock()

try:
    data = pd.read_csv('../Crop_recommendationV2.csv')
    temperature_data = data['temperature'].to_list()
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

def send_random_temperatures():
    while not FLAG:
        random_temperature = round(random.uniform(20, 25), 2)
        payload = json.dumps({"temperature": random_temperature})
        
        print(f"[Mosquitto] Publishing Cooling System Temp: {payload}")
        mosquitto_client.publish(MOSQUITTO_TOPIC, payload)
        thingsboard_client.publish(THINGSBOARD_TOPIC, payload)
        
        time.sleep(2)  

def on_message(client, userdata, msg):
    global FLAG
    try:
        message = msg.payload.decode().strip()
        print(f"\n[Received] Topic: {msg.topic} | Message: {message}")

        with flag_lock:
            if message == "TURNING THE COOLING SYSTEM ON":
                FLAG = False
                print("Cooling system activated. Sending acknowledgment.")
                mosquitto_client.publish(MOSQUITTO_ACK_TOPIC, "COOLING SYSTEM ACKNOWLEDGED")

                threading.Thread(target=send_random_temperatures, daemon=True).start()

            elif message == "TURNING THE COOLING SYSTEM OFF":
                FLAG = True
                print("Cooling system deactivated. Resuming normal operation.")

    except Exception as e:
        print(f"Error in on_message: {e}")

mosquitto_client.on_message = on_message
mosquitto_client.subscribe(MOSQUITTO_ALERT_TOPIC)

try:
    mosquitto_client.loop_start()

    while True:
        for temperature in temperature_data:
            while True:
                with flag_lock:
                    if FLAG:
                        break
                print("Cooling system is active...")
                time.sleep(1)
            
            try:
                payload = json.dumps({"temperature": temperature})
                print(f"[ThingsBoard] Publishing: {payload}")
                thingsboard_client.publish(THINGSBOARD_TOPIC, payload)
                
                print(f"[Mosquitto] Publishing: {payload}")
                mosquitto_client.publish(MOSQUITTO_TOPIC, payload)
                
                time.sleep(1)
            except Exception as e:
                print(f"Error publishing MQTT message: {e}")

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    mosquitto_client.loop_stop()
    mosquitto_client.disconnect()
    thingsboard_client.disconnect()
    print("MQTT Clients Disconnected. Exiting.")
