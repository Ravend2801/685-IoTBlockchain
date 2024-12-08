from flask import Flask, request, jsonify
from blockchain import Blockchain, Block
import time

# Initialize Flask app and blockchain
app = Flask(__name__)
iot_blockchain = Blockchain()

@app.route('/add_activity', methods=['POST'])
def add_activity():
    data = request.json
    device_id = data.get("device_id")
    activity = data.get("activity")

    if not device_id or not activity:
        return jsonify({"error": "Missing device_id or activity"}), 400

    new_block = Block(
        len(iot_blockchain.chain), 
        "", 
        time.time(), 
        {"device_id": device_id, "activity": activity}
    )
    iot_blockchain.add_block(new_block)
    return jsonify({"message": "Activity logged", "block_index": new_block.index, "hash": new_block.hash}), 201

@app.route('/get_chain', methods=['GET'])
def get_chain():
    chain_data = [
        {
            "index": block.index,
            "previous_hash": block.previous_hash,
            "timestamp": block.timestamp,
            "data": block.data,
            "hash": block.hash
        }
        for block in iot_blockchain.chain
    ]
    return jsonify({"chain": chain_data, "length": len(chain_data)})

@app.route('/is_chain_valid', methods=['GET'])
def is_chain_valid():
    valid = iot_blockchain.is_chain_valid()
    return jsonify({"valid": valid})

if __name__ == '__main__':
    app.run(debug=True)
