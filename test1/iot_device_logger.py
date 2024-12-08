from blockchain import Blockchain, Block
import time

# Initialize the blockchain
iot_blockchain = Blockchain()

def log_device_activity(device_id, activity):
    print(f"Logging activity for {device_id}: {activity}")
    new_block = Block(len(iot_blockchain.chain), "", time.time(), {"device_id": device_id, "activity": activity})
    iot_blockchain.add_block(new_block)
    print(f"Activity logged for {device_id} in block {new_block.index} with hash {new_block.hash}")

# Example usage
log_device_activity("device1", "Temperature: 22°C")
log_device_activity("device2", "Motion Detected")
