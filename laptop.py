import paho.mqtt.client as mqtt
import json
import time
from blockchain import Blockchain, Block

# Initialize Blockchain
blockchain = Blockchain()

# MQTT Broker Details
broker_address = "192.168.1.148"
broker_port = 1883
topic_update = "blockchain_update"
topic_sync = "blockchain_sync"
topic_sync_request = "blockchain_sync_request"

def on_connect(client, userdata, flags, rc):
    print("Laptop connected to broker with result code", rc)
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
            print("New block added to Laptop's blockchain.")
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
            print("Laptop updated its blockchain with the longest chain.")
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
        print("Laptop published full blockchain in response to sync request.")
    except Exception as e:
        print(f"Error responding to sync request: {e}")

def request_chain_sync(client, max_sync_attempts):
    try:
        print(f"Requesting blockchain sync. Remaining attempts: {max_sync_attempts}")
        client.publish(topic_sync_request, json.dumps({"requester": "Laptop", "attempts": max_sync_attempts}))
    except Exception as e:
        print(f"Error requesting chain sync: {e}")

def print_blockchain():
    print("\nCurrent Blockchain:")
    for block in blockchain.chain:
        print(block)

def main():
    client = mqtt.Client("LaptopNode")
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("david-pi", "super_secure_password")
    client.connect(broker_address, broker_port, 60)
    client.loop_start()

    try:
        while True:
            print_blockchain()
            time.sleep(10)
    except KeyboardInterrupt:
        print("Exiting Laptop...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
