
import os
import time
import ssl

import paho.mqtt.client as mqtt

from bottle import Bottle, run, request, template

from database import (
    initialize_database,
    insert_reading,
    get_readings
)


MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "broker")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "8883"))
MQTT_CA_CERT = os.getenv("MQTT_CA_CERT", "/app/certs/ca.crt")

TOPIC = "health/heart_rate"

app = Bottle()


# MQTT connection callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Application server connected to MQTT broker")

        client.subscribe(TOPIC)

        print(f"Subscribed to: {TOPIC}")
    else:
        print(f"Connection failed: {rc}")


# MQTT message callback
def on_message(client, userdata, message):
    try:
        payload = message.payload.decode("utf-8")

        device_id, heart_rate = payload.split(",")

        heart_rate = int(heart_rate)

        insert_reading(device_id, heart_rate)

        print(f"Received and stored: {device_id}, {heart_rate}")

    except Exception as error:
        print(f"Error processing message: {error}")


def start_mqtt():
    client = mqtt.Client(client_id="application-server" )

    tls_context = ssl.create_default_context(
        purpose=ssl.Purpose.SERVER_AUTH,
        cafile=MQTT_CA_CERT
    )

    tls_context.minimum_version = ssl.TLSVersion.TLSv1_2
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True

    client.tls_set_context(tls_context)

    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
            break

        except ssl.SSLError as exc:
            print(f"TLS connection failed: {exc}", flush=True)
            raise

        except OSError as exc:
            print(f"Broker unavailable: {exc}", flush=True)
            time.sleep(3)

    client.loop_start()

    return client


# Web dashboard
@app.route("/")
def dashboard():
    name = request.query.get("name", "").strip()

    readings = get_readings(name or None)

    return template(
        "dashboard",
        readings=readings,
        name=name
    )


if __name__ == "__main__":
    initialize_database()

    mqtt_client = start_mqtt()

    try:
        run(
            app,
            host="0.0.0.0",
            port=5000
        )

    finally:
        mqtt_client.disconnect()
        mqtt_client.loop_stop()
