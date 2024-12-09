import hashlib
import json
import time

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Calculate the SHA-256 hash of the block."""
        to_hash = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)  # Use sort_keys=True for consistent serialization
        return hashlib.sha256(to_hash.encode()).hexdigest()

    def to_dict(self):
        """Convert the block into a dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

    @staticmethod
    def from_dict(block_dict):
        """Reconstruct a Block object from a dictionary."""
        return Block(
            index=block_dict["index"],
            timestamp=block_dict["timestamp"],
            data=block_dict["data"],
            previous_hash=block_dict["previous_hash"]
        )

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
        """Add a new block to the blockchain."""
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
        """Validate the blockchain."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            # Check if the hash is correct
            if current.hash != current.calculate_hash():
                print(f"Invalid block at index {i}: hash does not match")
                return False
            # Check if the previous hash is correct
            if current.previous_hash != previous.hash:
                print(f"Invalid block at index {i}: previous hash does not match")
                return False
        return True

    def __repr__(self):
        return f"Blockchain(chain={self.chain})"

    def get_all_devices(self):
        """Retrive all devices and their associated data from the blockchain."""
        devices = []
        for block in self.chain: 
            for transaction in block['transactions'];
                if transaction['type'] == 'device_registration':
                    devices.append({
                        'device_id': transaction['device_id'],
                        'data': transaction['data']
                    })
        return devices 
