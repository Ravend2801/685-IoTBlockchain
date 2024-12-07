import paho.mqtt.client as mqtt
import json
import time
import adafruit_dht
import board
from blockchain import Blockchain

# Initialize Blockchain
blockchain = Blockchain()

# Initialize the DHT22 sensor on GPIO pin 17
dht_device = adafruit_dht.DHT22(board.D17)  # Set up DHT22 sensor

# MQTT Broker details
broker_address = "localhost"  # MQTT broker running on the same Raspberry Pi
broker_port = 1883  # Default MQTT port
topic_update = "blockchain_update"  # Topic for blockchain updates

# Callback function when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected to broker with result code {rc}")

# Publish a new block to the blockchain_update topic
def publish_new_block(client, block):
    block_data = json.dumps(block.__dict__)  # Serialize block data
    client.publish(topic_update, block_data)
    print(f"Published new block: {block_data}")

# Read sensor data from DHT22
def get_sensor_data():
    try:
        # Read temperature and humidity
        temperature_c = dht_device.temperature  # Temp in Celsius
        temperature_f = temperature_c * (9 / 5) + 32  # Convert to Fahrenheit
        humidity = dht_device.humidity

        # Return sensor data if valid
        if temperature_f is not None and humidity is not None:
            return {
                "temperature_f": round(temperature_f, 2),
                "humidity": round(humidity, 2)
            }
    except RuntimeError as err:
        print(f"Error reading sensor: {err.args[0]}")
        return None

def main():
    client = mqtt.Client("LaptopNode", callback_api_version=5)
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the MQTT broker
    client.connect(broker_address, broker_port, 60)

    # Start the MQTT loop
    client.loop_forever()

if __name__ == "__main__":
    main()
