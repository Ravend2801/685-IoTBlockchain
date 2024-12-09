import paho.mqtt.client as mqtt
import json
import time
from random import randint

# MQTT Broker details
broker_address = "192.168.1.148"
broker_port = 1883
topic_update = "blockchain_update"

def on_connect(client, userdata, flags, rc):
    print(f"Smart Solar Panel connected to broker with result code {rc}")

def publish_power_generation(client):
    watts = randint(100, 500)  # Simulate power generation in watts
    message = {
        "device": "smart_solar_panel",
        "data": {"watts": watts},
        "timestamp": time.time()
    }
    client.publish(topic_update, json.dumps(message))
    print(f"Smart Solar Panel reported: {message}")

def main():
    client = mqtt.Client("SmartSolarPanel")
    client.username_pw_set("david-pi", "super_secure_password")
    client.on_connect = on_connect

    client.connect(broker_address, broker_port, 60)
    client.loop_start()

    try:
        while True:
            publish_power_generation(client)
            time.sleep(15)  # Report every 15 seconds
    except KeyboardInterrupt:
        print("\nExiting Smart Solar Panel...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
