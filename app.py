from flask import Flask, jsonify
from blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/devices', methods=['GET'])
def get_devices():
    devices = blockchain.get_all_devices()
    return jsonify({'devices': devices})

if __name__ == '__main__':
    app.run(debug=True)
