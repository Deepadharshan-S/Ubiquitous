import paho.mqtt.client as mqtt
import json
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import THINGSBOARD_HOST, ACCESS_TOKEN


# Initialize MQTT client
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)

# Store actuator status
actuator_commands = {}

# Callback for receiving RPC commands (e.g., Cooling ON/OFF)
def on_message(client, userdata, msg):
    global actuator_commands
    payload = json.loads(msg.payload.decode())

    if "method" in payload:
        method = payload["method"]
        params = payload["params"]
        actuator_commands[method] = params
        print(f"Received command: {method} -> {params}")

# Connect to ThingsBoard
client.on_message = on_message
client.connect(THINGSBOARD_HOST, 1883, 60)
client.subscribe("v1/devices/me/rpc/request/+")  # Subscribe to RPC commands
client.loop_start()

def send_telemetry(data):
    """Send sensor data to ThingsBoard"""
    client.publish("v1/devices/me/telemetry", json.dumps(data))

def get_actuator_status(method):
    """Get the latest command for an actuator (e.g., 'ON' or 'OFF')"""
    return actuator_commands.get(method, "OFF")
