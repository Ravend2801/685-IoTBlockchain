import paho.mqtt.client as mqtt
import json
from blockchain import Blockchain, Block

# Initialize Blockchain
blockchain = Blockchain()

# MQTT Broker Details
broker_address = "192.168.1.148"  # Replace with your broker's IP
broker_port = 1883
topic_update = "blockchain_update"

# Callback when a message is received
def on_message(client, userdata, msg):
    global blockchain
    received_data = json.loads(msg.payload.decode())
    received_block = Block.from_dict(received_data)  # Reconstruct the block object

    # Validate and add block to the blockchain
    latest_block = blockchain.get_latest_block()
    if received_block.previous_hash == latest_block.hash and received_block.hash == received_block.calculate_hash():
        blockchain.chain.append(received_block)
        print(f"\nNew block received and added: {received_block}")
    else:
        print("\nInvalid block received, ignoring.")

    # Print the current blockchain
    print("\nCurrent Blockchain:")
    for block in blockchain.chain:
        print(block)

# Callback when connected to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(topic_update)
    else:
        print(f"Connection failed with code {rc}")

def main():
    # Set up the MQTT client
    client = mqtt.Client("LaptopNode")
    client.username_pw_set("david-pi", "super_secure_password")  # Add correct MQTT credentials
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the MQTT broker
    client.connect(broker_address, broker_port, 60)

    # Start the MQTT loop
    client.loop_forever()

if __name__ == "__main__":
    main()
