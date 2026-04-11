# Complete Assignment 6

# Calibrate Your Sensor

## Calibration Steps

I collected 3 soil samples with different wetness levels.
For each sample, I recorded the sensor reading, then weighed
the wet soil, dried it, and weighed again to calculate
the gravimetric soil moisture content.

## Calibration Data

| Sample | Sensor Reading (0-1023) | Weight Wet (g) | Weight Dry (g) | Soil Moisture % |
|--------|------------------------|----------------|----------------|-----------------|
| 1 (Dry)  | 198                  | 180            | 176            | 2.3%            |
| 2 (Damp) | 587                  | 205            | 191            | 7.3%            |
| 3 (Wet)  | 912                  | 230            | 208            | 10.6%           |

## Calculation Example (Sample 2)

- Wwet = 205g
- Wdry = 191g
- (205 - 191) / 191 × 100 = **7.3%**

## Calibration Graph

See calibrate.py — the script plots the calibration graph
and uses a best fit line to convert sensor readings to
soil moisture percentage.

## Calibrated Reading Result

Using the best fit line from the graph:
- Sensor reading 198  → Soil Moisture ≈ 2.3%
- Sensor reading 587  → Soil Moisture ≈ 7.3%
- Sensor reading 912  → Soil Moisture ≈ 10.6%