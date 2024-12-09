import paho.mqtt.client as mqtt
import json
import time
from blockchain import Blockchain

# Initialize Blockchain
blockchain = Blockchain()

# MQTT Broker details
broker_address = "192.168.1.148"
broker_port = 1883
topic_update = "blockchain_update"

def on_connect(client, userdata, flags, rc):
    print(f"Smart Lock connected to broker with result code {rc}")

def publish_block(client, block):
    """Publish the new block to the MQTT topic."""
    block_data = block.to_dict()
    client.publish(topic_update, json.dumps(block_data))
    print(f"Smart Lock published block: {block_data}")

def main():
    client = mqtt.Client("SmartLock")
    client.username_pw_set("david-pi", "super_secure_password")
    client.on_connect = on_connect

    client.connect(broker_address, broker_port, 60)
    client.loop_start()

    try:
        while True:
            # Generate lock status
            lock_status = {"status": "on" if int(time.time()) % 2 == 0 else "off"}

            # Add the data to the blockchain
            new_block = blockchain.add_block({
                "device": "smart_lock",
                "data": lock_status
            })

            # Publish the new block to the MQTT topic
            publish_block(client, new_block)

            time.sleep(10)  # Generate data every 10 seconds
    except KeyboardInterrupt:
        print("\nExiting Smart Lock...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
