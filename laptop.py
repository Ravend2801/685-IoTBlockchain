import paho.mqtt.client as mqtt
import json
import time
from blockchain import Blockchain, Block

# Initialize Blockchain
blockchain = Blockchain()
blockchain.register_device("laptop")  # Register this device

# MQTT Broker Details
broker_address = "192.168.1.148"
broker_port = 1883
topic_update = "blockchain_update"
topic_sync_request = "blockchain_sync_request"
topic_sync = "blockchain_sync"

def on_connect(client, userdata, flags, rc):
    print("Laptop connected to broker.")
    client.subscribe([(topic_update, 0), (topic_sync_request, 0), (topic_sync, 0)])

def on_message(client, userdata, msg):
    if msg.topic == topic_update:
        handle_block_update(client, json.loads(msg.payload.decode()))
    elif msg.topic == topic_sync_request:
        respond_to_sync_request(client)
    elif msg.topic == topic_sync:
        handle_chain_sync(client, json.loads(msg.payload.decode()))

def handle_block_update(client, block_data):
    """Try to add a received block to the chain."""
    try:
        received_block = Block.from_dict(block_data)
        latest_block = blockchain.get_latest_block()

        if validate_block(received_block, latest_block):
            blockchain.chain.append(received_block)
            print("Added received block to blockchain.")
        else:
            print("Invalid block received. Requesting sync.")
            request_chain_sync(client)
    except Exception as e:
        print(f"Error handling block update: {e}")

def respond_to_sync_request(client):
    """Respond to a sync request by sending the full blockchain."""
    chain_data = [block.to_dict() for block in blockchain.chain]
    client.publish(topic_sync, json.dumps(chain_data))
    print("Published full blockchain in response to sync request.")

def handle_chain_sync(client, chain_data):
    """Replace the local blockchain if the received chain is longer."""
    new_chain = [Block.from_dict(block) for block in chain_data]
    if blockchain.replace_chain(new_chain):
        print("Replaced local blockchain with the longest valid chain.")
    else:
        print("Received chain is invalid or not longer.")

def request_chain_sync(client):
    """Request the full blockchain from peers."""
    print("Requesting full blockchain sync.")
    client.publish(topic_sync_request, json.dumps({"requester": "laptop"}))

def validate_block(proposed_block, latest_block):
    """Validate a block based on hash and previous hash."""
    return (
        proposed_block.previous_hash == latest_block.hash
        and proposed_block.hash == proposed_block.calculate_hash()
    )

def print_blockchain():
    """Print the current blockchain."""
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
