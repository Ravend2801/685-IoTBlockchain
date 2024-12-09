import paho.mqtt.client as mqtt
import json
import time
import adafruit_dht
import board
from blockchain import Blockchain, Block

# Initialize Blockchain
blockchain = Blockchain()
blockchain.register_device("pi")  # Register this device

# Initialize the DHT22 sensor on GPIO pin 17
dht_device = adafruit_dht.DHT22(board.D17)

# MQTT Broker details
broker_address = "localhost"
broker_port = 1883
topic_proposal = "blockchain_proposal"
topic_update = "blockchain_update"
topic_sync_request = "blockchain_sync_request"
topic_sync = "blockchain_sync"

def on_connect(client, userdata, flags, rc):
    print("Pi connected to broker.")
    client.subscribe([(topic_proposal, 0), (topic_update, 0), (topic_sync_request, 0), (topic_sync, 0)])

def on_message(client, userdata, msg):
    if msg.topic == topic_proposal:
        handle_block_proposal(client, json.loads(msg.payload.decode()))
    elif msg.topic == topic_update:
        handle_block_update(client, json.loads(msg.payload.decode()))
    elif msg.topic == topic_sync_request:
        respond_to_sync_request(client)
    elif msg.topic == topic_sync:
        handle_chain_sync(json.loads(msg.payload.decode()))

def handle_block_proposal(client, proposal_data):
    try:
        proposed_block = Block.from_dict(proposal_data)
        latest_block = blockchain.get_latest_block()

        if blockchain.current_proposer == "pi" and validate_block(proposed_block, latest_block):
            blockchain.chain.append(proposed_block)
            print("Added proposed block to blockchain.")
            broadcast_block(client, proposed_block)
            blockchain.rotate_proposer()  # Rotate to the next proposer
        else:
            print("Block proposal rejected: Not Pi's turn or invalid block.")
    except Exception as e:
        print(f"Error processing block proposal: {e}")

def handle_block_update(client, block_data):
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
    chain_data = [block.to_dict() for block in blockchain.chain]
    client.publish(topic_sync, json.dumps(chain_data))
    print("Published full blockchain in response to sync request.")

def handle_chain_sync(chain_data):
    new_chain = [Block.from_dict(block) for block in chain_data]
    if blockchain.replace_chain(new_chain):
        print("Replaced local blockchain with the longest valid chain.")
    else:
        print("Received chain is invalid or not longer.")

def request_chain_sync(client):
    print("Requesting full blockchain sync.")
    client.publish(topic_sync_request, json.dumps({"requester": "pi"}))

def broadcast_block(client, block):
    block_data = block.to_dict()
    client.publish(topic_update, json.dumps(block_data))
    print("Broadcasted block to the network.")

def validate_block(proposed_block, latest_block):
    return (
        proposed_block.previous_hash == latest_block.hash
        and proposed_block.hash == proposed_block.calculate_hash()
    )

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

def propose_block(client, data):
    try:
        latest_block = blockchain.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=latest_block.hash
        )
        client.publish(topic_proposal, json.dumps(new_block.to_dict()))
        print("Proposed new block:", new_block.to_dict())
    except Exception as e:
        print(f"Error proposing block: {e}")

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
            if current_time - last_publish_time >= 10 and blockchain.current_proposer == "pi":
                sensor_data = get_sensor_data()
                if sensor_data:
                    propose_block(client, sensor_data)
                last_publish_time = current_time
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting Pi...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
