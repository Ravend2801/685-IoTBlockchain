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
        }, sort_keys=True)
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

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.device_list = []  # Track devices for round-robin proposer
        self.current_proposer = None

    def create_genesis_block(self):
        """Create a consistent Genesis Block."""
        return Block(
            index=0,
            timestamp=0,
            data="Genesis Block",
            previous_hash="0"
        )

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data, device_id):
        """Add a new block to the blockchain if it's this device's turn."""
        if self.current_proposer != device_id:
            raise Exception(f"Not {device_id}'s turn to propose a block.")
        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=latest_block.hash
        )
        if new_block.hash == new_block.calculate_hash():
            self.chain.append(new_block)
            self.rotate_proposer()  # Move to the next proposer
            return new_block
        else:
            raise Exception("Block validation failed.")

    def validate_chain(self, chain):
        """Validate an entire blockchain."""
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]
            if current.previous_hash != previous.hash or current.hash != current.calculate_hash():
                return False
        return True

    def replace_chain(self, new_chain):
        """Replace the chain with a new valid chain if it's longer."""
        if len(new_chain) > len(self.chain) and self.validate_chain(new_chain):
            self.chain = new_chain
            return True
        return False

    def register_device(self, device_id):
        """Register a device for round-robin proposing."""
        if device_id not in self.device_list:
            self.device_list.append(device_id)
            if not self.current_proposer:  # Set the first proposer
                self.current_proposer = device_id

    def rotate_proposer(self):
        """Move to the next proposer in the round-robin list."""
        if self.device_list:
            current_index = self.device_list.index(self.current_proposer)
            self.current_proposer = self.device_list[(current_index + 1) % len(self.device_list)]
