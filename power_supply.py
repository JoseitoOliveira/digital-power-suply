from abc import ABC, abstractmethod
from random import uniform
import time

class PowerSupply(ABC):
    """Abstract interface for power supplies"""
    
    @abstractmethod
    def connect(self):
        """Establishes connection with the power supply"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnects from the power supply"""
        pass
    
    @abstractmethod
    def set_voltage(self, voltage: float):
        """Sets the output voltage"""
        pass
    
    @abstractmethod
    def set_current(self, current: float):
        """Sets the current limit"""
        pass
    
    @abstractmethod
    def get_voltage(self) -> float:
        """Returns the current voltage"""
        pass
    
    @abstractmethod
    def get_current(self) -> float:
        """Returns the current reading"""
        pass
    
    @abstractmethod
    def output_on(self):
        """Turns the output ON"""
        pass
    
    @abstractmethod
    def output_off(self):
        """Turns the output OFF"""
        pass
    
    @abstractmethod
    def is_output_on(self) -> bool:
        """Checks if the output is ON"""
        pass


class MockPowerSupply(PowerSupply):
    """Mock implementation of power supply for development"""
    
    def __init__(self):
        # Configured values (setpoints)
        self.voltage_setpoint = 0.0
        self.current_limit = 0.0
        
        # Measured values
        self.measured_voltage = 0.0
        self.measured_current = 0.0
        
        self.output_enabled = False
        self.connected = False
        self.last_update = time.time()
        
        # Variable load simulation
        self.base_resistance = 2.0  # Base resistance in ohms
        self.noise_factor = 0.01    # Noise factor (1%)
    
    def connect(self):
        self.connected = True
    
    def disconnect(self):
        self.connected = False
        self.output_enabled = False
    
    def set_voltage(self, voltage: float):
        """Sets the voltage setpoint"""
        if voltage < 0 or voltage > 30:  # Simulating 30V limit
            raise ValueError("Voltage out of range (0-30V)")
        self.voltage_setpoint = voltage
    
    def set_current(self, current: float):
        """Sets the current limit"""
        if current < 0 or current > 5:  # Simulating 5A limit
            raise ValueError("Current out of range (0-5A)")
        self.current_limit = current
    
    def get_voltage(self) -> float:
        """Returns the voltage (setpoint when OFF, measured when ON)"""
        if not self.output_enabled:
            return self.voltage_setpoint
        return self.measured_voltage
    
    def get_current(self) -> float:
        """Returns the current (limit when OFF, measured when ON)"""
        if not self.output_enabled:
            return self.current_limit
        
        self._update_measurements()
        return self.measured_current
    
    def _update_measurements(self):
        """Updates internal measurements"""

        # Simulate load resistance variation
        current_resistance = self.base_resistance + uniform(-self.noise_factor * self.base_resistance, self.noise_factor * self.base_resistance)

        # Calculate current based on voltage and simulated resistance
        current = self.measured_voltage / max(0.1, current_resistance)  # avoid division by zero
        if current > self.current_limit:
            self.measured_current = self.current_limit
            self.measured_voltage = self.current_limit * self.base_resistance
            return
        
        self.measured_voltage = self.voltage_setpoint
        self.measured_current = current
    
    def output_on(self):
        """Turns the output ON and starts measurements"""
        self.output_enabled = True
    
    def output_off(self):
        """Turns the output OFF and resets measurements"""
        self.output_enabled = False
    
    def is_output_on(self) -> bool:
        """Returns the output state"""
        return self.output_enabled
