# app.py - Virtual IoT Device
import json, time, random
import paho.mqtt.client as mqtt

DEVICE_ID = "temp-alert-device"
TELEMETRY_TOPIC = DEVICE_ID + "/telemetry"
COMMAND_TOPIC = DEVICE_ID + "/commands"

led_on = False

def on_message(client, userdata, message):
    global led_on
    payload = json.loads(message.payload.decode())
    led_on = payload.get("led", False)
    print(f"LED {'ON' if led_on else 'OFF'}")

client = mqtt.Client(DEVICE_ID + "_client")
client.connect("test.mosquitto.org")
client.subscribe(COMMAND_TOPIC)
client.on_message = on_message
client.loop_start()

while True:
    temperature = round(random.uniform(28, 40), 1)
    telemetry = json.dumps(["temperature": temperature])
    client.publish(TELEMETRY_TOPIC, telemetry)
    print(f"[{telemetry}] LED: {'ON' if led_on else 'OFF'}")
    time.sleep(10)
