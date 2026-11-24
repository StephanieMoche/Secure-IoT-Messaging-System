
import os
import random
import time

import paho.mqtt.client as mqtt


BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "broker")
BROKER_PORT = 1883
TOPIC = "health/heart_rate"

USERS = ["John", "Jane", "Sarah", "Rob", "Steph"]


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print(f"Connection failed: {rc}")


def connect_to_broker(client):
    while True:
        try:
            client.connect(BROKER_HOST, BROKER_PORT, 60)
            return
        except OSError:
            print("Waiting for MQTT broker...")
            time.sleep(3)


def main():
    client = mqtt.Client(client_id="raspberry-pi-simulator")
    client.on_connect = on_connect

    connect_to_broker(client)
    client.loop_start()

    try:
        while True:
            for user in USERS:
                heart_rate = random.randint(60, 100)

                message = f"{user},{heart_rate}"

                result = client.publish(TOPIC, message)
                result.wait_for_publish()

                print(f"Published: {message}")

            time.sleep(5)

    except KeyboardInterrupt:
        print("Stopping device simulator")

    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()
