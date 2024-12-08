from flask import Flask, render_template
from blockchain import Blockchain  # Import your blockchain module

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)


# Assume blockchain instance is initialized here
blockchain = Blockchain()

@app.route('/blockchain_status')
def blockchain_status():
    last_block = blockchain.get_last_block()
    return {'latest_block_hash': last_block.hash}
