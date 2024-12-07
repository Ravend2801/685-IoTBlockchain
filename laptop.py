import paho.mqtt.client as mqtt
import json
from blockchain import Blockchain, Block

# Initialize Blockchain
blockchain = Blockchain()

# MQTT Broker Details
broker_address = "192.168.1.148"  # Replace with your broker's IP
broker_port = 1883
topic_update = "blockchain_update"
topic_sync = "blockchain_sync"
sync_complete = False  # Flag to indicate synchronization

# Validate the blockchain
def validate_chain(chain):
    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i - 1]
        if current.previous_hash != previous.hash or current.hash != current.calculate_hash():
            return False
    return True

# Callback for blockchain updates
def on_message_block_update(client, userdata, msg):
    global blockchain, sync_complete
    if not sync_complete:
        print("Ignoring block updates until synchronization is complete.")
        return

    received_data = json.loads(msg.payload.decode())
    received_block = Block.from_dict(received_data)

    # Validate and append the block
    latest_block = blockchain.get_latest_block()
    if (
        received_block.previous_hash == latest_block.hash and
        received_block.hash == received_block.calculate_hash()
    ):
        blockchain.chain.append(received_block)
        print(f"\nNew block received and added: {received_block}")
    else:
        print(f"\nInvalid block received, ignoring. Previous hash mismatch or invalid block hash.")

    # Print the current blockchain
    print("\nCurrent Blockchain:")
    for block in blockchain.chain:
        print(block)

# Callback for blockchain synchronization
def on_message_chain_sync(client, userdata, msg):
    global blockchain, sync_complete
    received_chain_data = json.loads(msg.payload.decode())
    new_chain = [Block.from_dict(block) for block in received_chain_data]

    # Validate and update the chain if it's valid and longer
    if len(new_chain) > len(blockchain.chain) and validate_chain(new_chain):
        blockchain.chain = new_chain
        sync_complete = True  # Mark synchronization as complete
        print("\nBlockchain synchronized successfully.")
    else:
        print("\nReceived blockchain is invalid or shorter, ignoring.")

# Callback when connected to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(topic_update)  # Subscribe to individual block updates
        client.subscribe(topic_sync)    # Subscribe to full blockchain syncs
    else:
        print(f"Connection failed with code {rc}")

def main():
    client = mqtt.Client("LaptopNode")
    client.username_pw_set("david-pi", "super_secure_password")
    client.on_connect = on_connect
    client.message_callback_add(topic_update, on_message_block_update)
    client.message_callback_add(topic_sync, on_message_chain_sync)

    client.connect(broker_address, broker_port, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()
