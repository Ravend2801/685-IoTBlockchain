import paho.mqtt.client as mqtt
import json
import time

# MQTT Broker details
broker_address = "localhost"
broker_port = 1883
topic_update = "blockchain_update"

def on_connect(client, userdata, flags, rc):
    print(f"Malicious User connected to broker with result code {rc}")

def send_fake_message(client):
    fake_message = {
        "device": "smart_lock",
        "data": {"status": "off"},  # Fake "off" message
        "timestamp": time.time()
    }
    client.publish(topic_update, json.dumps(fake_message))
    print(f"Malicious User sent fake message: {fake_message}")

def main():
    client = mqtt.Client("MaliciousUser")
    client.username_pw_set("malicious-user", "not_so_secure_password")
    client.on_connect = on_connect

    client.connect(broker_address, broker_port, 60)
    client.loop_start()

    try:
        while True:
            send_fake_message(client)
            time.sleep(20)  # Attempt an attack every 20 seconds
    except KeyboardInterrupt:
        print("\nExiting Malicious User...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
