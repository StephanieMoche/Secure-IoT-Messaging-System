
import os
import time

import paho.mqtt.client as mqtt

from bottle import Bottle, run, request, template

from database import (
    initialize_database,
    insert_reading,
    get_readings
)


BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "broker")
BROKER_PORT = 1883
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
    client = mqtt.Client(
        client_id="application-server"
    )

    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            client.connect(BROKER_HOST, BROKER_PORT, 60)
            break

        except OSError:
            print("Waiting for MQTT broker...")
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
