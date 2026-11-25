
import os
import random
import time
import ssl

import paho.mqtt.client as mqtt


MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "broker")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "8883"))
MQTT_CA_CERT = os.getenv("MQTT_CA_CERT", "/app/certs/ca.crt")

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
            client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
            return

        except ssl.SSLError as exc:
            print(f"TLS connection failed: {exc}", flush=True)
            raise

        except OSError:
            print("Waiting for MQTT broker...")
            time.sleep(3)


def main():
    client = mqtt.Client(client_id="raspberry-pi-simulator")

    tls_context = ssl.create_default_context(
        purpose=ssl.Purpose.SERVER_AUTH,
        cafile=MQTT_CA_CERT
    )

    tls_context.minimum_version = ssl.TLSVersion.TLSv1_2
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True

    client.tls_set_context(tls_context)


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
