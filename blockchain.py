import hashlib
import time

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        to_hash = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(to_hash.encode()).hexdigest()

    def __repr__(self):
        return (f"Block(index={self.index}, timestamp={self.timestamp}, data={self.data}, "
                f"previous_hash={self.previous_hash}, hash={self.hash})")

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        """Create a consistent Genesis Block."""
        return Block(
            index=0,
            timestamp=0,  # Fixed timestamp for consistency
            data="Genesis Block",
            previous_hash="0"
        )

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=latest_block.hash
        )
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            # Validate current block's hash
            if current.hash != current.calculate_hash():
                print(f"Invalid block at index {i}: hash does not match")
                return False

            # Validate hash link to previous block
            if current.previous_hash != previous.hash:
                print(f"Invalid block at index {i}: previous hash does not match")
                return False

        return True

    def __repr__(self):
        return f"Blockchain(chain={self.chain})"
