import paho.mqtt.client as mqtt
import json
import time
from blockchain import Blockchain, Block

blockchain = Blockchain()
broker_address = "192.168.1.148"
broker_port = 1883
topic_update = "blockchain_update"
topic_sync = "blockchain_sync"

def on_connect(client, userdata, flags, rc):
    print("Smart Lock connected to broker.")
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
        print("New block added to Smart Lock's blockchain.")
    else:
        print("Invalid block received by Smart Lock.")

def handle_chain_sync(chain_data):
    new_chain = [Block.from_dict(block) for block in chain_data]
    if len(new_chain) > len(blockchain.chain) and blockchain.is_chain_valid():
        blockchain.chain = new_chain
        print("Smart Lock updated its blockchain with the longest chain.")

def publish_block(client, block):
    block_data = block.to_dict()
    client.publish(topic_update, json.dumps(block_data))
    print(f"Smart Lock published block: {block_data}")

def main():
    client = mqtt.Client("SmartLock")
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("david-pi", "super_secure_password")
    client.connect(broker_address, broker_port, 60)
    client.loop_start()

    try:
        while True:
            lock_status = {"status": "on" if int(time.time()) % 2 == 0 else "off"}
            new_block = blockchain.add_block({"device": "smart_lock", "data": lock_status})
            publish_block(client, new_block)
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nExiting Smart Lock...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
