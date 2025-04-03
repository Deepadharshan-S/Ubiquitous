import os
import json
import time
import random
import joblib
import argparse
import paho.mqtt.client as mqtt
import pandas as pd

# ThingsBoard Configuration
THINGSBOARD_HOST = "demo.thingsboard.io"  # Change if using local ThingsBoard
THINGSBOARD_ACCESS_TOKEN = "NBEchWjACWf0v5hnBKwv"  # Replace with your device token
THINGSBOARD_TOPIC = "v1/devices/me/telemetry"

# Load Model
try:
    model = joblib.load("crop_model.pkl")  # Load the trained model
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)
    
try:
    data = pd.read_csv("Crop_recommendationV2.csv")  # Adjust path if needed
except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit(1)


# Define Thresholds for Different Crops
CROP_THRESHOLDS = {}
for crop in data["label"].unique():
    crop_data = data[data["label"] == crop]

    # Calculate dynamic thresholds
    temp_threshold = round(crop_data["temperature"].median(), 2)
    humidity_threshold = round(crop_data["humidity"].median(), 2)

    # Set CO₂ dynamically (assuming a range, can be adjusted based on actual values)
    co2_threshold = round(380 + (humidity_threshold / 2))  # Example dynamic formula

    CROP_THRESHOLDS[crop] = {
        "TEMP_THRESHOLD": temp_threshold,
        "HUMIDITY_THRESHOLD": humidity_threshold,
        "CO2_THRESHOLD": co2_threshold,
    }

# Read CSV and Sample Random Values
try:
    data = pd.read_csv("Crop_recommendationV2.csv")  # Adjust path as needed
    N = random.choice(data["N"].tolist())
    P = random.choice(data["P"].tolist())
    K = random.choice(data["K"].tolist())
    ph = round(random.uniform(data["ph"].min(), data["ph"].max()), 2)
    rainfall = round(random.uniform(data["rainfall"].min(), data["rainfall"].max()), 2)
    temperature = round(random.uniform(data["temperature"].min(), data["temperature"].max()), 2)
    humidity = round(random.uniform(data["humidity"].min(), data["humidity"].max()), 2)
except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit(1)

# Argument Parser
parser = argparse.ArgumentParser()
parser.add_argument("--show-climate", action="store_true", help="Show climate conditions without setting thresholds")
parser.add_argument("--set-thresholds", type=str, help="Set thresholds for the given crop")
args = parser.parse_args()

if args.show_climate:
    # Show climate conditions
    print("\n--- Current Environment Conditions ---")
    print(f"N: {N}\nP: {P}\nK: {K}\nTemperature: {temperature}\nHumidity: {humidity}\nPh: {ph}\nRainfall: {rainfall}\n")

    # Predict Crop
    input_features = [[N, P, K, temperature, humidity, ph, rainfall]]
    try:
        recommended_crop = model.predict(input_features)[0]
        print(f"Recommended Crop based on environment: {recommended_crop}")
    except Exception as e:
        print(f"Error during prediction: {e}")
        exit(1)
    exit(0)

if args.set_thresholds:
    crop = args.set_thresholds.lower()
    if crop in CROP_THRESHOLDS:
        thresholds = CROP_THRESHOLDS[crop]
        print(f'export TEMP_THRESHOLD={thresholds["TEMP_THRESHOLD"]}')
        print(f'export HUMIDITY_THRESHOLD={thresholds["HUMIDITY_THRESHOLD"]}')
        print(f'export CO2_THRESHOLD={thresholds["CO2_THRESHOLD"]}')
    else:
        print("Invalid crop selection.")
        exit(1)
    exit(0)

# Publish Data to ThingsBoard
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # Use latest API version
    client.username_pw_set(THINGSBOARD_ACCESS_TOKEN)
    client.connect(THINGSBOARD_HOST, 1883, 60)

    payload = json.dumps({
        "N": N, "P": P, "K": K,
        "temperature": temperature, "humidity": humidity,
        "pH": ph, "rainfall": rainfall
    })

    client.publish(THINGSBOARD_TOPIC, payload)
    print(f"Published Recommendation to ThingsBoard: {payload}")

    time.sleep(1)  # Ensure message is sent before disconnecting
    client.disconnect()
except Exception as e:
    print(f"Error publishing to ThingsBoard: {e}")
    exit(1)
