import paho.mqtt.client as mqtt
import time
import json
import threading
import os

MOSQUITTO_HOST = "localhost"
MOSQUITTO_PORT = 1883
MOSQUITTO_TOPIC = "sensor/readings"
MOSQUITTO_ALERT_TOPIC = "sensor/alerts"
MOSQUITTO_ACK_TOPIC = "sensor/ack"

ack_lock = threading.Lock()
ack_received = False  

HUMIDITY_THRESHOLD = int(os.getenv("HUMIDITY_THRESHOLD", 50)) 

class HumidityControlSystem:
    def __init__(self):
        self.window = []
        self.mqtt_client = mqtt.Client()
        self.status = False  

        try:
            self.mqtt_client.connect(MOSQUITTO_HOST, MOSQUITTO_PORT, 60)
        except Exception as e:
            print(f"MQTT connection error: {e}")
            exit(1)

        self.mqtt_client.on_message = self.on_ack_message
        self.mqtt_client.subscribe(MOSQUITTO_ACK_TOPIC)
        self.mqtt_client.loop_start()

    def on_ack_message(self, client, userdata, msg):
        global ack_received
        message = msg.payload.decode().strip()
        if message == "HUMIDIFIER ACKNOWLEDGED":
            with ack_lock:
                ack_received = True
            print("[ACK] Humidifier Acknowledged.")

    def add_humidity_level(self, humidity_level):
        self.window.append(humidity_level)
        if len(self.window) > 20:
            self.window.pop(0)
        print(self.window)
        if self.window: 
            avg_humidity = sum(self.window) / len(self.window)
            print(f"Avg Humidity Level: {avg_humidity:.2f}%")

            if avg_humidity < HUMIDITY_THRESHOLD and not self.status:
                self.send_alert()  # Humidifier ON
            elif avg_humidity >= HUMIDITY_THRESHOLD and self.status:
                self.turn_off_humidifier()  # Humidifier OFF

    def send_alert(self):
        global ack_received
        if not self.status:
            print("Humidifier ON!")
            ack_received = False  
            while not ack_received:
                self.mqtt_client.publish(MOSQUITTO_ALERT_TOPIC, "TURNING HUMIDIFIER ON")
                print("Sent alert: TURNING HUMIDIFIER ON")
                time.sleep(2)  

            self.status = True  

    def turn_off_humidifier(self):
        if self.status:
            print("Humidifier OFF!")
            self.mqtt_client.publish(MOSQUITTO_ALERT_TOPIC, "TURNING HUMIDIFIER OFF")
            self.status = False  


actuator = HumidityControlSystem()


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())  

        if "humidity" in data:
            humidity_level = float(data["humidity"])
            print(f"Humidity Level: {humidity_level}%")
            actuator.add_humidity_level(humidity_level)

    except Exception as e:
        print(f"Error processing message: {e}")


mosquitto_client = mqtt.Client()
mosquitto_client.on_message = on_message

try:
    mosquitto_client.connect(MOSQUITTO_HOST, MOSQUITTO_PORT, 60)
    mosquitto_client.subscribe(MOSQUITTO_TOPIC)
    mosquitto_client.loop_start()

    print(f"Subscribed to {MOSQUITTO_TOPIC}. Waiting for messages...")

    while True:
        time.sleep(2)

except KeyboardInterrupt:
    print("\nShutting down...")

finally:
    mosquitto_client.loop_stop()
    mosquitto_client.disconnect()
    print("MQTT Disconnected. Exiting.")
