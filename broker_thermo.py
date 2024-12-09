import paho.mqtt.client as mqtt
import json
import time
import adafruit_dht
import board
from blockchain import Blockchain, Block

# Initialize Blockchain
blockchain = Blockchain()

# Initialize the DHT22 sensor
dht_device = adafruit_dht.DHT22(board.D17)

# MQTT Broker details
broker_address = "localhost"
broker_port = 1883
topic_update = "blockchain_update"
topic_sync = "blockchain_sync"
topic_sync_request = "blockchain_sync_request"

def on_connect(client, userdata, flags, rc):
    print("Pi connected to broker with result code", rc)
    client.subscribe([(topic_update, 0), (topic_sync, 0), (topic_sync_request, 0)])

def on_message(client, userdata, msg):
    if msg.topic == topic_update:
        handle_block_update(client, json.loads(msg.payload.decode()))
    elif msg.topic == topic_sync:
        handle_chain_sync(client, json.loads(msg.payload.decode()))
    elif msg.topic == topic_sync_request:
        handle_sync_request(client)

def handle_block_update(client, block_data, max_sync_attempts=3):
    try:
        received_block = Block.from_dict(block_data)
        latest_block = blockchain.get_latest_block()

        if received_block.previous_hash == latest_block.hash and received_block.hash == received_block.calculate_hash():
            blockchain.chain.append(received_block)
            print("New block added to Pi's blockchain.")
        else:
            print("Invalid block received. Requesting full chain...")
            request_chain_sync(client, max_sync_attempts)
    except Exception as e:
        print(f"Error handling block update: {e}")
        request_chain_sync(client, max_sync_attempts)

def handle_chain_sync(client, chain_data, max_sync_attempts=3):
    try:
        new_chain = [Block.from_dict(block) for block in chain_data]
        if len(new_chain) > len(blockchain.chain) and blockchain.is_chain_valid():
            blockchain.chain = new_chain
            print("Pi updated its blockchain with the longest chain.")
        else:
            print("Received chain is invalid or not longer. Requesting chain sync again...")
            if max_sync_attempts > 0:
                request_chain_sync(client, max_sync_attempts - 1)
    except Exception as e:
        print(f"Error handling chain sync: {e}")
        if max_sync_attempts > 0:
            request_chain_sync(client, max_sync_attempts - 1)

def handle_sync_request(client):
    try:
        chain_data = [block.to_dict() for block in blockchain.chain]
        client.publish(topic_sync, json.dumps(chain_data))
        print("Pi published full blockchain in response to sync request.")
    except Exception as e:
        print(f"Error responding to sync request: {e}")

def request_chain_sync(client, max_sync_attempts):
    try:
        print(f"Requesting blockchain sync. Remaining attempts: {max_sync_attempts}")
        client.publish(topic_sync_request, json.dumps({"requester": "Pi", "attempts": max_sync_attempts}))
    except Exception as e:
        print(f"Error requesting chain sync: {e}")

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

def publish_new_block(client, data):
    try:
        new_block = blockchain.add_block(data)
        block_data = new_block.to_dict()
        client.publish(topic_update, json.dumps(block_data))
        print("Pi published new block:", block_data)
    except Exception as e:
        print(f"Error publishing new block: {e}")

def main():
    client = mqtt.Client("PiNode")
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("david-pi", "super_secure_password")
    client.connect(broker_address, broker_port, 60)
    client.loop_start()

    try:
        last_publish_time = 0
        while True:
            current_time = time.time()
            if current_time - last_publish_time >= 10:
                sensor_data = get_sensor_data()
                if sensor_data:
                    publish_new_block(client, sensor_data)
                last_publish_time = current_time
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting Pi...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
