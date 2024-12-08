from pi import pi_blockchain
from laptop import laptop_blockchain

# Check the integrity of both blockchains
def test_blockchain(blockchain, label):
    if blockchain.is_chain_valid():
        print(f"{label} Blockchain is valid.")
    else:
        print(f"{label} Blockchain integrity compromised.")

test_blockchain(pi_blockchain, "Pi")
test_blockchain(laptop_blockchain, "Laptop")

# Print the blockchain blocks
def print_blockchain(blockchain, label):
    print(f"\n{label} Blockchain:")
    for block in blockchain.chain:
        print(f"Block {block.index}: {block.transactions}")

print_blockchain(pi_blockchain, "Pi")
print_blockchain(laptop_blockchain, "Laptop")
