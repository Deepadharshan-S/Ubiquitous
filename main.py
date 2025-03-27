import subprocess

print("Starting Smart Farming System...")

subprocess.Popen(["python3", "utils/thingsboard_mqtt.py"])
subprocess.Popen(["python3", "sensors/temperature_sensor.py"])
subprocess.Popen(["python3", "actuators/cooling_system.py"])
