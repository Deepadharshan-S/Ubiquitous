#!/bin/bash
source venv/bin/activate

# Get climate conditions and recommended crop
climate_output=$(python3 main.py --show-climate)  # Run main.py to display conditions

# Display climate conditions and recommended crop
echo "------------------------------------"
echo "Climate Conditions & Recommendation:"
echo "$climate_output" | grep -E "N:|P:|K:|Temperature:|Humidity:|Ph:|Rainfall:|Recommended Crop based on environment:"
echo "------------------------------------"

# Get user input after displaying climate conditions
echo -n "Enter crop (or press Enter to use recommended crop): "
read crop

# If user didn't enter a crop, use the recommended one
if [ -z "$crop" ]; then
    crop=$(echo "$climate_output" | grep "Recommended Crop" | awk -F': ' '{print $2}')
    echo "Using recommended crop: $crop"
fi

# Get and apply environment variables
env_vars=$(python3 main.py --set-thresholds "$crop")  # Pass input to Python script
if [ -z "$env_vars" ]; then
    echo "Invalid crop. Exiting..."
    exit 1
fi

eval "$env_vars"  # Apply environment variables

# Verify variables are set
echo "Thresholds set:"
echo "TEMP_THRESHOLD=$TEMP_THRESHOLD"
echo "HUMIDITY_THRESHOLD=$HUMIDITY_THRESHOLD"
echo "CO2_THRESHOLD=$CO2_THRESHOLD"

# Start all environment sensors
gnome-terminal -- bash -c "export TEMP_THRESHOLD=$TEMP_THRESHOLD; export HUMIDITY_THRESHOLD=$HUMIDITY_THRESHOLD; export CO2_THRESHOLD=$CO2_THRESHOLD; python3 sensors/environment_sensors/co2_sensor.py; exec bash"
gnome-terminal -- bash -c "export TEMP_THRESHOLD=$TEMP_THRESHOLD; export HUMIDITY_THRESHOLD=$HUMIDITY_THRESHOLD; export CO2_THRESHOLD=$CO2_THRESHOLD; python3 sensors/environment_sensors/humidity_sensor.py; exec bash"
gnome-terminal -- bash -c "export TEMP_THRESHOLD=$TEMP_THRESHOLD; export HUMIDITY_THRESHOLD=$HUMIDITY_THRESHOLD; export CO2_THRESHOLD=$CO2_THRESHOLD; python3 sensors/environment_sensors/temperature_sensor.py; exec bash"

# Start all actuators
gnome-terminal -- bash -c "export TEMP_THRESHOLD=$TEMP_THRESHOLD; export HUMIDITY_THRESHOLD=$HUMIDITY_THRESHOLD; export CO2_THRESHOLD=$CO2_THRESHOLD; python3 actuators/surrounding/cooling_system.py; exec bash"
gnome-terminal -- bash -c "export TEMP_THRESHOLD=$TEMP_THRESHOLD; export HUMIDITY_THRESHOLD=$HUMIDITY_THRESHOLD; export CO2_THRESHOLD=$CO2_THRESHOLD; python3 actuators/surrounding/humidifier.py; exec bash"
gnome-terminal -- bash -c "export TEMP_THRESHOLD=$TEMP_THRESHOLD; export HUMIDITY_THRESHOLD=$HUMIDITY_THRESHOLD; export CO2_THRESHOLD=$CO2_THRESHOLD; python3 actuators/surrounding/ventilation_system.py; exec bash"

echo "All scripts have been started in separate terminals."
