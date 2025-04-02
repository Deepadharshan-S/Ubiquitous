import os

# Define thresholds for different crops
CROP_THRESHOLDS = {
    "carrot": {"temperature": 22, "humidity": 50, "co2": 600},
    "beans": {"temperature": 25, "humidity": 55, "co2": 700},
    "tomato": {"temperature": 26, "humidity": 60, "co2": 750},
}

def set_environment_variables(crop):
    if crop in CROP_THRESHOLDS:
        thresholds = CROP_THRESHOLDS[crop]
        os.environ["TEMP_THRESHOLD"] = str(thresholds["temperature"])
        os.environ["HUMIDITY_THRESHOLD"] = str(thresholds["humidity"])
        os.environ["CO2_THRESHOLD"] = str(thresholds["co2"])
        print(f"Thresholds set for {crop}: {thresholds}")
    else:
        print("Invalid crop selected. Available options:", ", ".join(CROP_THRESHOLDS.keys()))

if __name__ == "__main__":
    crop = input("Enter crop name (carrot, beans, tomato): ").strip().lower()
    set_environment_variables(crop)
