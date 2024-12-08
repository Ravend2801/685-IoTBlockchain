from blockchain import Blockchain, Block
import time

# Initialize the blockchain
pi_blockchain = Blockchain()

# Function to simulate adding transactions from the Pi
def add_transaction(data):
    last_block = pi_blockchain.get_last_block()
    new_block = Block(index=last_block.index + 1, transactions=[data], timestamp=time.time(), previous_hash=last_block.hash)
    pi_blockchain.add_block(new_block)

# Example usage
add_transaction("Pi Sensor data - Temp: 25C")
