import paho.mqtt.client as mqtt
import time
import json
import threading

MOSQUITTO_HOST = "localhost"
MOSQUITTO_PORT = 1883
MOSQUITTO_TOPIC = "sensor/readings"
MOSQUITTO_ALERT_TOPIC = "sensor/alerts"
MOSQUITTO_ACK_TOPIC = "sensor/ack"  

CO2_THRESHOLD = 400  # ppm (parts per million)

ack_lock = threading.Lock()
ack_received = False  


class VentilationSystem:
    def __init__(self):
        self.co2_levels = []
        self.mqtt_client = mqtt.Client()
        self.ventilation_status = False  # False = OFF, True = ON

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
        if message == "VENTILATION SYSTEM ACKNOWLEDGED":
            with ack_lock:
                ack_received = True
            print("[ACK] Ventilation System Acknowledged.")

    def add_co2_level(self, co2_level):
        self.co2_levels.append(co2_level)
        if len(self.co2_levels) > 20:
            self.co2_levels.pop(0)
        
        avg_co2 = sum(self.co2_levels) / len(self.co2_levels)
        print(f"Avg CO₂ Level: {avg_co2:.2f} ppm")

        if avg_co2 >= CO2_THRESHOLD and not self.ventilation_status:
            self.activate_ventilation()
        elif avg_co2 < CO2_THRESHOLD and self.ventilation_status:
            self.deactivate_ventilation()

    def activate_ventilation(self):
        global ack_received
        if not self.ventilation_status:
            print("Ventilation System ON!")
            ack_received = False 
            while not ack_received:
                self.mqtt_client.publish(MOSQUITTO_ALERT_TOPIC, "TURNING VENTILATION ON")
                print("Sent alert: TURNING VENTILATION ON")
                time.sleep(1)  

            self.ventilation_status = True 

    def deactivate_ventilation(self):
        if self.ventilation_status:
            print("Ventilation System OFF!")
            self.mqtt_client.publish(MOSQUITTO_ALERT_TOPIC, "TURNING VENTILATION OFF")
            self.ventilation_status = False  


ventilation_system = VentilationSystem()


def on_message(client, userdata, msg):
    try:
        print(f"\n[Received] {msg.topic} | {msg.payload.decode()}\n")
        data = json.loads(msg.payload.decode())  

        if "CO2" in data:
            co2_level = float(data["CO2"])
            print(f"CO₂ Level: {co2_level} ppm")
            ventilation_system.add_co2_level(co2_level)

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
        time.sleep(1)

except KeyboardInterrupt:
    print("\nShutting down...")

finally:
    mosquitto_client.loop_stop()
    mosquitto_client.disconnect()
    print("MQTT Disconnected. Exiting.")
