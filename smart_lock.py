import paho.mqtt.client as mqtt
import json
import time
from random import choice

# MQTT Broker details
broker_address = "192.168.1.148"
broker_port = 1883
topic_update = "blockchain_update"

def on_connect(client, userdata, flags, rc):
    print(f"Smart Lock connected to broker with result code {rc}")

def publish_lock_status(client):
    lock_status = choice(["on", "off"])  # Randomly simulate lock status
    message = {
        "device": "smart_lock",
        "data": {"status": lock_status},
        "timestamp": time.time()
    }
    client.publish(topic_update, json.dumps(message))
    print(f"Smart Lock reported: {message}")

def main():
    client = mqtt.Client("SmartLock")
    client.username_pw_set("david-pi", "super_secure_password")
    client.on_connect = on_connect

    client.connect(broker_address, broker_port, 60)
    client.loop_start()

    try:
        while True:
            publish_lock_status(client)
            time.sleep(10)  # Report every 10 seconds
    except KeyboardInterrupt:
        print("\nExiting Smart Lock...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
