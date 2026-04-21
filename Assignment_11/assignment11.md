# Investigate Other GPS Data

## Additional NMEA Data Beyond location

GPS sensors send NMEA sentences containing more than just latitude and longitude. I investigated the following:

### 1. Date and Time (from $GPMIC sentence)
GPS signals include precise UTC date and time.
This can be used to set the clock on microcontroller
without needing NTP, which is useful in remote areas
without internet access.

Example NMEA: $GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
- Time: 12:35:19 UTC
- Date: 23rd March 1994

### 2. Elevation / Altitude (from $GPGGA sentence)
The $GPGGA sentence includes altitude above sea level in meters.
Useful for tracking delivery vehicles in hilly terrain or
monitoring drones.

Example: $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
- Altitude: 545.4 meters above sea level

### 3. Speed (from $GPRMC sentence)
Speed over ground in knots is included in $GPRMC.
Convert to km/h: speed_kmh = speed_knots * 1.852
Useful for fleet tracking – alert if vehicle exceeds
the speed limit.

## Using This Data in the IoT Device

I updated the telemetry payload to include altitude and speed:

```python
telemetry = json.dumps({
    "latitude": gps_data["lat"],
    "longitude": gps_data["lon"],
    "altitude": gps_data["altitude"],
    "speed_kmh": gps_data["speed"] * 1.852,
    "timestamp": gps_data["time"]
})
```
