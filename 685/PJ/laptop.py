from blockchain import Blockchain, Block
import time

# Initialize the blockchain
laptop_blockchain = Blockchain()

# Function to simulate adding transactions from the laptop
def add_transaction(data):
    last_block = laptop_blockchain.get_last_block()
    new_block = Block(index=last_block.index + 1, transactions=[data], timestamp=time.time(), previous_hash=last_block.hash)
    laptop_blockchain.add_block(new_block)

# Example usage
add_transaction("Laptop control command - Adjust Temperature")
