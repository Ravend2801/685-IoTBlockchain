import paho.mqtt.client as mqtt
import json
from blockchain import Blockchain, Block

blockchain = Blockchain()
broker_address = "192.168.1.148"
broker_port = 1883
topic_update = "blockchain_update"
topic_sync = "blockchain_sync"

def on_connect(client, userdata, flags, rc):
    print("Laptop connected to broker.")
    client.subscribe([(topic_update, 0), (topic_sync, 0)])

def on_message(client, userdata, msg):
    if msg.topic == topic_update:
        handle_block_update(json.loads(msg.payload.decode()))
    elif msg.topic == topic_sync:
        handle_chain_sync(json.loads(msg.payload.decode()))

def handle_block_update(block_data):
    received_block = Block.from_dict(block_data)
    latest_block = blockchain.get_latest_block()

    if received_block.previous_hash == latest_block.hash and received_block.hash == received_block.calculate_hash():
        blockchain.chain.append(received_block)
        print("New block added to Laptop's blockchain.")
    else:
        print("Invalid block received by Laptop.")

    print_blockchain()

def handle_chain_sync(chain_data):
    new_chain = [Block.from_dict(block) for block in chain_data]
    if len(new_chain) > len(blockchain.chain) and blockchain.is_chain_valid():
        blockchain.chain = new_chain
        print("Laptop updated its blockchain with the longest chain.")

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
    client.loop_forever()

if __name__ == "__main__":
    main()
