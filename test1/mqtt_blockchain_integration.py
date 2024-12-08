import paho.mqtt.client as mqtt
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from iot_device_logger import log_device_activity

# Generate RSA keys
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# MQTT setup
broker = "test.mosquitto.org"
port = 1883
topic = "iot/device/data"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker!")
    client.subscribe(topic)

def on_message(client, userdata, message):
    encrypted_message = message.payload
    print("Received encrypted data:", encrypted_message)

    # Decrypt the message
    decrypted_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    print("Decrypted message:", decrypted_message.decode())
    log_device_activity("device1", decrypted_message.decode())

# MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port, 60)

client.loop_start()

# Example secure message
def simulate_device_activity():
    data = "Temperature: 24°C"
    encrypted_data = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    client.publish(topic, encrypted_data)
    print("Encrypted data sent!")

simulate_device_activity()
