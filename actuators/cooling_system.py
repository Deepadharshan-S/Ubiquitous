import paho.mqtt.client as mqtt

# MQTT Configuration
THINGSBOARD_HOST = "demo.thingsboard.io"
ACCESS_TOKEN = "aYjzIENDYsDlM0hreMl7"  # Replace with your actual token
ACTUATOR_TOPIC = "v1/devices/me/rpc/request/+"  # Subscribe to RPC commands

# Mosquitto Configuration (Local)
MOSQUITTO_BROKER = "localhost"
MOSQUITTO_PORT = 1883
MOSQUITTO_TOPIC = "actuators/cooling"

# MQTT Clients
thingsboard_client = mqtt.Client()
thingsboard_client.username_pw_set(ACCESS_TOKEN)

mosquitto_client = mqtt.Client()
mosquitto_client.connect(MOSQUITTO_BROKER, MOSQUITTO_PORT, 60)

def on_message(client, userdata, msg):
    """Handle messages from ThingsBoard and forward to Mosquitto."""
    command = msg.payload.decode().strip()
    print(f"Received from ThingsBoard: {command}")

    if "temperature more than 25" in command:
        print("🔥 High Temperature Alert! Turning Cooling System ON.")
        mosquitto_client.publish(MOSQUITTO_TOPIC, "on")
    else:
        print("❄️ Temperature Normal. Cooling System OFF.")
        mosquitto_client.publish(MOSQUITTO_TOPIC, "off")

def listen_for_alerts():
    """Subscribe to ThingsBoard alerts."""
    thingsboard_client.on_message = on_message
    thingsboard_client.connect(THINGSBOARD_HOST, 1883, 60)
    thingsboard_client.subscribe(ACTUATOR_TOPIC)
    thingsboard_client.loop_forever()

if __name__ == '__main__':
    listen_for_alerts()
