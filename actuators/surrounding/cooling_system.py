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

TEMPERATURE_THRESHOLD = int(os.getenv("TEMP_THRESHOLD", 25))

class CoolingSystem:
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
        if message == "COOLING SYSTEM ACKNOWLEDGED":
            with ack_lock:
                ack_received = True
            print("[ACK] Cooling System Acknowledged.")

    def add_temperature(self, temperature):
        self.window.append(temperature)
        if len(self.window) > 20:
            self.window.pop(0)
        print(self.window)
        if self.window: 
            avg_temp = sum(self.window) / len(self.window)
            print(f"Avg Temp: {avg_temp:.2f}°C")

            if avg_temp >= TEMPERATURE_THRESHOLD and not self.status:
                self.send_alert()  # Cooling ON
            elif avg_temp < TEMPERATURE_THRESHOLD and self.status:
                self.turn_off_cooling()  # Cooling OFF

    def send_alert(self):
        global ack_received
        if not self.status:
            print("Cooling System ON!")
            ack_received = False 
            while not ack_received:
                self.mqtt_client.publish(MOSQUITTO_ALERT_TOPIC, "TURNING THE COOLING SYSTEM ON")
                print("Sent alert: TURNING THE COOLING SYSTEM ON")
                time.sleep(2)  

            self.status = True 

    def turn_off_cooling(self):
        
        if self.status:
            print("Cooling System OFF!")
            self.mqtt_client.publish(MOSQUITTO_ALERT_TOPIC, "TURNING THE COOLING SYSTEM OFF")
            self.status = False  


actuator = CoolingSystem()


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())  

        if "temperature" in data:
            temperature = float(data["temperature"])
            print(f"Temperature: {temperature}°C")
            actuator.add_temperature(temperature)

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
