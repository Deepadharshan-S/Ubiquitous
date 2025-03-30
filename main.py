import multiprocessing
import time
import os
from sensors import co2_sensor, temperature_sensor
from actuators import ventilation_system, cooling_system

def run_sensor(sensor_func, name):
    """Wrapper function to run a sensor/actuator"""
    print(f"Starting {name} (PID: {os.getpid()})")
    sensor_func()

if __name__ == "__main__":
    multiprocessing.set_start_method("fork", force=True)  # 'fork' ensures real parallel execution

    # Create processes for each sensor/actuator
    processes = [
        multiprocessing.Process(target=run_sensor, args=(co2_sensor.main, "CO2 Sensor"), name="CO2_Sensor"),
        multiprocessing.Process(target=run_sensor, args=(temperature_sensor.main, "Temperature Sensor"), name="Temperature_Sensor"),
        multiprocessing.Process(target=run_sensor, args=(ventilation_system.main, "Ventilation System"), name="Ventilation_System"),
        multiprocessing.Process(target=run_sensor, args=(cooling_system.main, "Cooling System"), name="Cooling_System"),
    ]

    # Start all processes
    for process in processes:
        process.start()

    # Monitor processes and keep the main process alive
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[Stopping] Terminating all processes...")
        for process in processes:
            process.terminate()
        for process in processes:
            process.join()
        print("[Stopped] All processes terminated.")
