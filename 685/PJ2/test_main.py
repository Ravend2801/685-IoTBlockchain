import time
import random
from blockchain import Blockchain

# Initialize the blockchain
blockchain = Blockchain()

def generate_random_message():
    """Generate a random test message."""
    messages = [
        "Hello, Blockchain!",
        "Temperature: 22.5°C",
        "Humidity: 60%",
        "Random Data: 12345",
        "Test Message",
        "Blockchain Rocks!"
    ]
    return random.choice(messages)

def write_to_blockchain():
    """Write a new random message to the blockchain."""
    message = generate_random_message()
    new_block = blockchain.add_block({"message": message})
    print(f"New block added: {new_block}")

def print_blockchain():
    """Print the entire blockchain."""
    print("\nCurrent Blockchain:")
    for block in blockchain.chain:
        print(block)

def main():
    last_block_time = time.time()
    
    # Main loop
    while True:
        current_time = time.time()

        # Add a new block every 5 seconds
        if current_time - last_block_time >= 5:
            write_to_blockchain()
            last_block_time = current_time

        # Print the blockchain every second
        print_blockchain()
        time.sleep(1)

if __name__ == "__main__":
    main()
