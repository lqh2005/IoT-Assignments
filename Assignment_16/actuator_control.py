"""
Actuator Control Module
Simulates controlling physical actuators (LEDs, buzzer, relay)
In real deployment, this would interface with GPIO pins
"""

import time
from typing import Dict, Any
from enum import Enum


class ActuatorType(Enum):
    """Types of actuators"""
    LED = "led"
    BUZZER = "buzzer"
    RELAY = "relay"
    MOTOR = "motor"


class ActuatorController:
    """
    Control physical actuators based on IoT device state
    Simulates GPIO control for:
    - RGB LED (Red, Green, Yellow)
    - Buzzer/Speaker
    - Relay (for motor/pump control)
    """
    
    def __init__(self, simulate=True):
        """
        Initialize actuator controller
        
        Args:
            simulate: If True, simulate actuators; if False, use real GPIO
        """
        self.simulate = simulate
        self.state = {
            'led_red': False,
            'led_green': False,
            'led_yellow': False,
            'buzzer': False,
            'relay': False,
            'motor': False
        }
        
        # For simulation: track state history
        self.history = []
        
        if not simulate:
            try:
                # Real GPIO import (requires RPi.GPIO or board-specific library)
                import RPi.GPIO as GPIO
                self.gpio = GPIO
                self.gpio.setmode(GPIO.BCM)
                print("✅ Using real GPIO (Raspberry Pi detected)")
            except ImportError:
                print("⚠️ RPi.GPIO not available, using simulator mode")
                self.simulate = True
        
        self._log_state("initialized")
    
    def set_led(self, color: str, state: bool) -> Dict[str, Any]:
        """
        Control RGB LED
        
        Args:
            color: 'red', 'green', or 'yellow'
            state: True to turn on, False to turn off
            
        Returns:
            Status dict
        """
        
        led_key = f'led_{color.lower()}'
        
        if led_key not in self.state:
            return {'error': f'Unknown LED color: {color}'}
        
        self.state[led_key] = state
        status = 'ON' if state else 'OFF'
        
        action = f"LED({color.upper()}): {status}"
        self._log_state(action)
        
        if self.simulate:
            print(f"  💡 [SIM] {action}")
        else:
            self._gpio_set_pin(self._get_gpio_pin(led_key), state)
            print(f"  💡 {action}")
        
        return {
            'device': led_key,
            'state': state,
            'status': status,
            'timestamp': time.time()
        }
    
    def buzzer(self, state: bool, duration: float = 0.5) -> Dict[str, Any]:
        """
        Control buzzer/speaker
        
        Args:
            state: True to beep, False to silence
            duration: Duration of beep in seconds
            
        Returns:
            Status dict
        """
        
        self.state['buzzer'] = state
        
        if state:
            action = f"BUZZER: BEEP ({duration}s)"
            self._log_state(action)
            
            if self.simulate:
                print(f"  🔔 [SIM] {action}")
                # Simulate beep with visual feedback
                for _ in range(int(duration * 2)):
                    print("  🔔 BEEP!")
                    time.sleep(duration / 2)
            else:
                self._gpio_buzzer_beep(duration)
                print(f"  🔔 {action}")
        else:
            action = "BUZZER: OFF"
            self._log_state(action)
            
            if self.simulate:
                print(f"  🔔 [SIM] {action}")
            else:
                self._gpio_set_pin(self._get_gpio_pin('buzzer'), False)
                print(f"  🔔 {action}")
        
        return {
            'device': 'buzzer',
            'state': state,
            'duration': duration,
            'timestamp': time.time()
        }
    
    def relay(self, state: bool) -> Dict[str, Any]:
        """
        Control relay (for motor/pump/valve)
        
        Args:
            state: True to activate, False to deactivate
            
        Returns:
            Status dict
        """
        
        self.state['relay'] = state
        status = 'ON' if state else 'OFF'
        action = f"RELAY: {status}"
        
        self._log_state(action)
        
        if self.simulate:
            print(f"  🔌 [SIM] {action}")
        else:
            self._gpio_set_pin(self._get_gpio_pin('relay'), state)
            print(f"  🔌 {action}")
        
        return {
            'device': 'relay',
            'state': state,
            'status': status,
            'timestamp': time.time()
        }
    
    def motor(self, speed: int = 100) -> Dict[str, Any]:
        """
        Control motor speed using PWM
        
        Args:
            speed: Motor speed 0-100% (0 = off, 100 = full speed)
            
        Returns:
            Status dict
        """
        
        if not (0 <= speed <= 100):
            return {'error': 'Speed must be between 0 and 100'}
        
        self.state['motor'] = speed > 0
        action = f"MOTOR: {speed}%"
        
        self._log_state(action)
        
        if self.simulate:
            print(f"  ⚙️ [SIM] {action}")
        else:
            self._gpio_set_pwm(self._get_gpio_pin('motor'), speed)
            print(f"  ⚙️ {action}")
        
        return {
            'device': 'motor',
            'speed': speed,
            'state': speed > 0,
            'timestamp': time.time()
        }
    
    def emergency_stop(self) -> Dict[str, Any]:
        """Emergency stop - turn off all actuators"""
        
        print(f"\n🚨 EMERGENCY STOP - Shutting down all actuators")
        
        self.set_led('red', False)
        self.set_led('green', False)
        self.set_led('yellow', False)
        self.buzzer(False)
        self.relay(False)
        self.motor(0)
        
        self._log_state("emergency_stop")
        
        return {'status': 'all_actuators_off'}
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state of all actuators"""
        
        return {
            'timestamp': time.time(),
            'actuators': self.state.copy()
        }
    
    def get_history(self, limit: int = None) -> list:
        """Get history of actuator state changes"""
        
        if limit:
            return self.history[-limit:]
        return self.history.copy()
    
    def _log_state(self, action: str):
        """Log state change for debugging"""
        
        log_entry = {
            'timestamp': time.time(),
            'action': action,
            'state': self.state.copy()
        }
        self.history.append(log_entry)
    
    def _get_gpio_pin(self, device: str) -> int:
        """Map device name to GPIO pin number (Raspberry Pi BCM)"""
        
        pin_map = {
            'led_red': 17,
            'led_green': 27,
            'led_yellow': 22,
            'buzzer': 23,
            'relay': 24,
            'motor': 25
        }
        
        return pin_map.get(device, None)
    
    def _gpio_set_pin(self, pin: int, state: bool):
        """Set GPIO pin state (real hardware)"""
        
        if not self.gpio:
            return
        
        try:
            self.gpio.setup(pin, self.gpio.OUT)
            self.gpio.output(pin, self.gpio.HIGH if state else self.gpio.LOW)
        except Exception as e:
            print(f"GPIO Error: {e}")
    
    def _gpio_set_pwm(self, pin: int, duty_cycle: int):
        """Set GPIO pin PWM (for motor speed control)"""
        
        if not self.gpio:
            return
        
        try:
            self.gpio.setup(pin, self.gpio.OUT)
            pwm = self.gpio.PWM(pin, 50)  # 50Hz frequency
            pwm.start(duty_cycle)
        except Exception as e:
            print(f"PWM Error: {e}")
    
    def _gpio_buzzer_beep(self, duration: float):
        """Create buzzer beep (real hardware)"""
        
        pin = self._get_gpio_pin('buzzer')
        if not pin:
            return
        
        self._gpio_set_pin(pin, True)
        time.sleep(duration)
        self._gpio_set_pin(pin, False)


class ActuatorSequence:
    """Helper class to execute predefined actuator sequences"""
    
    def __init__(self, controller: ActuatorController):
        self.controller = controller
    
    def alert_sequence(self, severity: str = 'warning'):
        """
        Execute alert sequence based on severity
        
        Args:
            severity: 'critical', 'warning', 'info'
        """
        
        if severity == 'critical':
            # Fast red blinking + continuous beep
            print("🚨 CRITICAL ALERT SEQUENCE")
            for _ in range(5):
                self.controller.set_led('red', True)
                time.sleep(0.2)
                self.controller.set_led('red', False)
                time.sleep(0.2)
            self.controller.buzzer(True, 1.0)
            
        elif severity == 'warning':
            # Yellow LED + 3 beeps
            print("⚠️ WARNING ALERT SEQUENCE")
            self.controller.set_led('yellow', True)
            for _ in range(3):
                self.controller.buzzer(True, 0.2)
                time.sleep(0.3)
            
        elif severity == 'info':
            # Green LED + 1 beep
            print("ℹ️ INFO ALERT SEQUENCE")
            self.controller.set_led('green', True)
            self.controller.buzzer(True, 0.1)
    
    def harvest_ready_sequence(self):
        """Sequence when fruit is ready to harvest"""
        
        print("✅ HARVEST READY SEQUENCE")
        self.controller.set_led('green', True)
        for _ in range(2):
            self.controller.buzzer(True, 0.3)
            time.sleep(0.2)
        self.controller.relay(True)  # Activate conveyor/transport
        time.sleep(2)
        self.controller.relay(False)


def demo():
    """Demonstrate actuator control"""
    
    print("🎮 Actuator Control Demo")
    print("=" * 70)
    
    # Initialize controller (simulator mode)
    controller = ActuatorController(simulate=True)
    
    # Test 1: LED control
    print("\n1️⃣ LED Control Test")
    print("-" * 70)
    controller.set_led('green', True)
    time.sleep(1)
    controller.set_led('green', False)
    controller.set_led('red', True)
    time.sleep(1)
    controller.set_led('red', False)
    controller.set_led('yellow', True)
    time.sleep(1)
    
    # Test 2: Buzzer
    print("\n2️⃣ Buzzer Control Test")
    print("-" * 70)
    controller.set_led('yellow', False)
    controller.buzzer(True, 0.5)
    time.sleep(1)
    
    # Test 3: Relay
    print("\n3️⃣ Relay Control Test")
    print("-" * 70)
    controller.relay(True)
    time.sleep(1)
    controller.relay(False)
    
    # Test 4: Motor
    print("\n4️⃣ Motor Speed Control Test")
    print("-" * 70)
    controller.motor(50)
    time.sleep(1)
    controller.motor(100)
    time.sleep(1)
    controller.motor(0)
    
    # Test 5: Alert sequences
    print("\n5️⃣ Alert Sequences Test")
    print("-" * 70)
    sequence = ActuatorSequence(controller)
    sequence.alert_sequence('info')
    time.sleep(1)
    sequence.alert_sequence('warning')
    time.sleep(1)
    
    # Get state
    print("\n6️⃣ Current State")
    print("-" * 70)
    state = controller.get_state()
    print(f"Actuators: {state['actuators']}")
    
    # Emergency stop
    print("\n7️⃣ Emergency Stop")
    print("-" * 70)
    controller.emergency_stop()
    
    print("\n✅ Demo complete")


if __name__ == '__main__':
    demo()
