import os

CROP_THRESHOLDS = {
    "carrot": {"TEMP_THRESHOLD": 20, "HUMIDITY_THRESHOLD": 50, "CO2_THRESHOLD": 400},
    "beans": {"TEMP_THRESHOLD": 25, "HUMIDITY_THRESHOLD": 60, "CO2_THRESHOLD": 450},
    "tomato": {"TEMP_THRESHOLD": 22, "HUMIDITY_THRESHOLD": 55, "CO2_THRESHOLD": 420},
}

def set_environment_variables(crop):
    if crop in CROP_THRESHOLDS:
        thresholds = CROP_THRESHOLDS[crop]
        os.environ["TEMP_THRESHOLD"] = str(thresholds["TEMP_THRESHOLD"])
        os.environ["HUMIDITY_THRESHOLD"] = str(thresholds["HUMIDITY_THRESHOLD"])
        os.environ["CO2_THRESHOLD"] = str(thresholds["CO2_THRESHOLD"])

        # Print only export commands (no extra text)
        print(f'export TEMP_THRESHOLD={thresholds["TEMP_THRESHOLD"]}')
        print(f'export HUMIDITY_THRESHOLD={thresholds["HUMIDITY_THRESHOLD"]}')
        print(f'export CO2_THRESHOLD={thresholds["CO2_THRESHOLD"]}')
    else:
        exit(1)  # Exit with error code if crop is invalid

if __name__ == "__main__":
    crop = input().strip().lower()  # Read input without a prompt message
    set_environment_variables(crop)
