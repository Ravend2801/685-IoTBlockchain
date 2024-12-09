import paho.mqtt.client as mqtt
import json
import time
import adafruit_dht
import board
from blockchain import Blockchain, Block

# Initialize Blockchain
blockchain = Blockchain()

# Initialize the DHT22 sensor on GPIO pin 17
dht_device = adafruit_dht.DHT22(board.D17)

# MQTT Broker details
broker_address = "localhost"
broker_port = 1883
topic_update = "blockchain_update"
topic_sync = "blockchain_sync"

def on_connect(client, userdata, flags, rc):
    print(f"Pi connected to broker with result code {rc}")
    client.subscribe([(topic_update, 0), (topic_sync, 0)])

def on_message(client, userdata, msg):
    """Handle incoming messages for blockchain updates and synchronization."""
    if msg.topic == topic_update:
        handle_block_update(json.loads(msg.payload.decode()))
    elif msg.topic == topic_sync:
        handle_chain_sync(json.loads(msg.payload.decode()))

def handle_block_update(block_data):
    received_block = Blockchain.from_dict(block_data)
    latest_block = blockchain.get_latest_block()

    if received_block.previous_hash == latest_block.hash and received_block.hash == received_block.calculate_hash():
        blockchain.chain.append(received_block)
        print("New block added to Pi's blockchain.")
    else:
        print("Invalid block received by Pi.")

def handle_chain_sync(chain_data):
    new_chain = [Block.from_dict(block) for block in chain_data]
    if len(new_chain) > len(blockchain.chain) and blockchain.is_chain_valid():
        blockchain.chain = new_chain
        print("Pi updated its blockchain with the longest chain.")

def publish_new_block(client, block):
    block_data = block.to_dict()
    client.publish(topic_update, json.dumps(block_data))
    print(f"Pi published new block: {block_data}")

def broadcast_full_chain(client):
    chain_data = [block.to_dict() for block in blockchain.chain]
    client.publish(topic_sync, json.dumps(chain_data))
    print("Pi broadcasted full blockchain.")

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
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("david-pi", "super_secure_password")
    client.connect(broker_address, broker_port, 60)
    client.loop_start()

    try:
        last_temperature_time = 0
        last_broadcast_time = 0

        while True:
            current_time = time.time()

            # Publish temperature data every 10 seconds
            if current_time - last_temperature_time >= 10:
                sensor_data = get_sensor_data()
                if sensor_data:
                    new_block = blockchain.add_block(sensor_data)
                    publish_new_block(client, new_block)
                last_temperature_time = current_time

            # Broadcast full blockchain every 30 seconds
            if current_time - last_broadcast_time >= 1:
                broadcast_full_chain(client)
                last_broadcast_time = current_time

            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
