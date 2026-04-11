import matplotlib.pyplot as plt
import numpy as np

# ── Calibration data ──────────────────────────────────────
sensor_readings  = [198, 587, 912]
moisture_percent = [2.3, 7.3, 10.6]

# ── Best fit line ─────────────────────────────────────────
coeffs   = np.polyfit(sensor_readings, moisture_percent, 1)
best_fit = np.poly1d(coeffs)

x_line = np.linspace(0, 1023, 300)
y_line = best_fit(x_line)

# ── Plot ──────────────────────────────────────────────────
plt.figure(figsize=(10, 6))
plt.scatter(sensor_readings, moisture_percent,
            color='blue', s=100, zorder=5, label='Calibration samples')
plt.plot(x_line, y_line,
         color='red', linewidth=2, label='Best fit line')

# Add annotations for each point
for x, y in zip(sensor_readings, moisture_percent):
    plt.annotate(f'({x}, {y}%)',
                 xy=(x, y),
                 xytext=(x + 30, y + 0.3),
                 fontsize=10,
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

plt.xlabel('Sensor Reading (0–1023)', fontsize=12)
plt.ylabel('Gravimetric Soil Moisture (%)', fontsize=12)
plt.title('Soil Moisture Sensor Calibration', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('calibration_graph.png', dpi=150, bbox_inches='tight')
print('✓ Graph saved to calibration_graph.png')
plt.show()

print('\n' + '='*50)
print('Soil Moisture Sensor Calibration Results')
print('='*50)

# ── Convert any sensor value to moisture % ────────────────
def get_moisture_percent(sensor_value):
    return round(float(best_fit(sensor_value)), 2)

# Print calibration samples
print('\nCalibration Samples:')
print('-' * 50)
for i, reading in enumerate(sensor_readings, 1):
    expected = moisture_percent[i-1]
    calculated = get_moisture_percent(reading)
    print(f'{i}. Sensor Reading: {reading:3d} → Expected: {expected:5.1f}% | Calculated: {calculated:5.2f}%')

# Print best fit line coefficients
print('\n' + '-' * 50)
print('Best Fit Line Equation:')
print('-' * 50)
print(f'Moisture % = {coeffs[0]:.8f} × SensorReading + {coeffs[1]:.8f}')
print(f'\nSimplified: moisture = {coeffs[0]:.6f} * sensor + {coeffs[1]:.4f}')