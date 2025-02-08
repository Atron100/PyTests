import pyvisa

class PowerSuplly():   
    def __init__(self):
        pass

    def register_commands(self):
        # Registers the commands for controlling the power supply
        return {
            'PS_SETUP_VOLTAGE': self.setup_voltage,
            'PS_SETUP_CURRENT': self.setup_current,
            'PS_POWER_ON': self.power_on,
            'PS_POWER_OFF': self.power_off
        }

    # Additional methods for handling communication with the power supply
    # For example:
    def setup_voltage(self, voltage, channel):
        # Logic to set the voltage
        
        pass

    def setup_current(self, current, channel):
        # Logic to set the current
        pass

    def power_on(self, onof):
        # Logic to power on the device
        pass

    def power_off(self):
        # Logic to power off the device
        pass

    def close_connection(self):
        pass



