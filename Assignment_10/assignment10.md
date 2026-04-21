# Build a New IoT Device

## Device Design

I built a temperature-controlled LED alert system.
- **Sensor:** DHT11 temperature sensor
- **Actuator:** LED (lights up when temperature is too high)
- **Threshold:** LED turns ON when temperature > 35°C
- **Cloud:** Telemetry sent to Azure IoT Hub,
Azure Function controls the LED via command messages
