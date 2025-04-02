import time
import pandas as pd
import paho.mqtt.client as mqtt
import json
import random
import threading

THINGSBOARD_HOST = "demo.thingsboard.io"
THINGSBOARD_ACCESS_TOKEN = "in75gn0cpos84fphb8g1"
THINGSBOARD_TOPIC = "v1/devices/me/telemetry"

MOSQUITTO_HOST = "localhost"
MOSQUITTO_PORT = 1883
MOSQUITTO_TOPIC = "sensor/readings"
MOSQUITTO_ALERT_TOPIC = "sensor/alerts"
MOSQUITTO_ACK_TOPIC = "sensor/ack"  # New topic for acknowledgment


FLAG = True
flag_lock = threading.Lock()

try:
    data = pd.read_csv('/home/deepadharshan/Downloads/Ubiquitous/Crop_recommendationV2.csv')
    co2_data = data['co2_concentration'].to_list()
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

def send_random_concentrations():
    while not FLAG:
        random_temperature = round(random.uniform(300, 350), 2)
        payload = json.dumps({"CO2": random_temperature})
        
        print(f"[Mosquitto] Publishing Ventilation System Concentration: {payload}")
        mosquitto_client.publish(MOSQUITTO_TOPIC, payload)
        thingsboard_client.publish(THINGSBOARD_TOPIC, payload)
        
        time.sleep(2)  

def on_message(client, userdata, msg):
    global FLAG
    try:
        message = msg.payload.decode().strip()
        print(f"\n[Received] Topic: {msg.topic} | Message: {message}")

        with flag_lock:
            if message == "TURNING VENTILATION ON":
                FLAG = False
                print("Ventilation system activated. Sending acknowledgment.")
                mosquitto_client.publish(MOSQUITTO_ACK_TOPIC, "VENTILATION SYSTEM ACKNOWLEDGED")

                threading.Thread(target=send_random_concentrations, daemon=True).start()

            elif message == "TURNING VENTILATION OFF":
                FLAG = True
                print("Ventilation system deactivated. Resuming normal operation.")

    except Exception as e:
        print(f"Error in on_message: {e}")

mosquitto_client.on_message = on_message
mosquitto_client.subscribe(MOSQUITTO_ALERT_TOPIC)

try:
    mosquitto_client.loop_start()

    while True:
        for sample in co2_data:
            while True:
                with flag_lock:
                    if FLAG:
                        break
                print("Ventilation system is active...")
                time.sleep(2)
            
            try:
                payload = json.dumps({"CO2": sample})
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
