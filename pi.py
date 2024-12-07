import paho.mqtt.client as mqtt
import json
import time
import adafruit_dht
import board
from blockchain import Blockchain

# Initialize Blockchain
blockchain = Blockchain()

# Initialize the DHT22 sensor on GPIO pin 17
dht_device = adafruit_dht.DHT22(board.D17)

# MQTT Broker details
broker_address = "localhost"
broker_port = 1883
topic_update = "blockchain_update"
topic_sync = "blockchain_sync"

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected to broker with result code {rc}")

# Publish a new block to the blockchain_update topic
def publish_new_block(client, block):
    block_data = block.to_dict()
    client.publish(topic_update, json.dumps(block_data))
    print(f"Published new block: {block_data}")

# Broadcast the entire blockchain to the blockchain_sync topic
def broadcast_full_chain(client):
    chain_data = [block.to_dict() for block in blockchain.chain]
    client.publish(topic_sync, json.dumps(chain_data))
    print(f"Broadcasted full blockchain: {chain_data}")

# Read sensor data
def get_sensor_data():
    try:
        temperature_c = dht_device.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dht_device.humidity
        if temperature_f is not None and humidity is not None:
            return {"temperature_f": round(temperature_f, 2), "humidity": round(humidity, 2)}
    except RuntimeError as err:
        print(f"Error reading sensor: {err.args[0]}")
    return None

def main():
    client = mqtt.Client("PiNode")
    client.username_pw_set("david-pi", "super_secure_password")
    client.on_connect = on_connect

    try:
        client.connect(broker_address, broker_port, 60)
        client.loop_start()

        while True:
            # Publish individual blocks
            sensor_data = get_sensor_data()
            if sensor_data:
                new_block = blockchain.add_block(sensor_data)
                publish_new_block(client, new_block)

            # Periodically broadcast the full blockchain
            if int(time.time()) % 30 == 0:  # Every 30 seconds
                broadcast_full_chain(client)

            time.sleep(10)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
