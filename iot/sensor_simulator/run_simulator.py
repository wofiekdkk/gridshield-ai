"""
Sensor Simulator - Zero-Dependency standard-library HTTP Publisher
"""
import time
import random
import math
import urllib.request
import json
from datetime import datetime

API_URL = "http://localhost:8000/api/v1/sensors/ingest"

SENSORS = [
    {"sensor_id": "SUB_A_LINE_01", "component_id": "LINE_1", "base_v": 230, "base_i": 100, "base_load": 65},
    {"sensor_id": "SUB_A_LINE_02", "component_id": "LINE_2", "base_v": 231, "base_i": 110, "base_load": 70},
    {"sensor_id": "SUB_B_LINE_03", "component_id": "LINE_3", "base_v": 229, "base_i": 95,  "base_load": 60},
    {"sensor_id": "SUB_B_LINE_07", "component_id": "LINE_7", "base_v": 230, "base_i": 140, "base_load": 72},
    {"sensor_id": "TRAFO_T1",      "component_id": "TRAFO_0", "base_v": 230, "base_i": 180, "base_load": 68},
    {"sensor_id": "GEN_MAIN",      "component_id": "GEN_1",  "base_v": 230, "base_i": 300, "base_load": 75},
]

def generate_reading(sensor, t):
    daily = 10 * math.sin(2 * math.pi * (t % 300) / 300)
    noise_v = random.uniform(-1.5, 1.5)
    noise_i = random.uniform(-3, 3)
    noise_t = random.uniform(-0.5, 0.5)

    voltage = sensor["base_v"] + noise_v + daily * 0.1
    load = max(10, min(95, sensor["base_load"] + daily + random.uniform(-2, 2)))
    current = sensor["base_i"] * (load / sensor["base_load"]) + noise_i
    power = voltage * current * 0.95 / 1000
    temperature = 35 + load * 0.3 + noise_t

    return {
        "sensor_id": sensor["sensor_id"],
        "component_id": sensor["component_id"],
        "voltage": round(voltage, 2),
        "current": round(current, 2),
        "frequency": round(50.0 + random.uniform(-0.05, 0.05), 2),
        "active_power": round(power, 2),
        "reactive_power": round(power * 0.3, 2),
        "temperature": round(temperature, 2),
        "power_factor": round(0.93 + random.uniform(-0.02, 0.02), 3),
        "load_percentage": round(load, 2),
        "breaker_status": "ON",
        "line_status": "NORMAL",
        "status": "NORMAL",
    }

def main():
    print("GridShield Sensor Simulator - Ready")
    print(f"Target Service: {API_URL}")
    print("-" * 50)
    t = 0
    while True:
        for s in SENSORS:
            try:
                reading = generate_reading(s, t)
                data_bytes = json.dumps(reading).encode("utf-8")
                
                # Zero-dependency HTTP POST fallback
                req = urllib.request.Request(
                    API_URL, 
                    data=data_bytes, 
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=3) as res:
                    res.read()
            except Exception as e:
                print(f"[{s['sensor_id']}] POST Failed: {e}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Pushed metric set to control center.")
        t += 1
        time.sleep(2)

if __name__ == "__main__":
    main()
