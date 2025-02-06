import pyvisa

class PowerSuplly():
    def __init__(self):
        # Initialize the power supply communication here (e.g., VISA connection setup)
        #self.power_supply = PowerSupplyConnection()  # Assuming you have a class for handling the connection
        COMMANDS = {
            'PS_SETUP_VOLTAGE': 'setup_voltage',
            'PS_SETUP_CURRENT': 'setup_current',
            'PS_POWER_ON': 'power_on',
            'PS_POWER_OFF': 'power_off'
        }

    

    def register_commands(self):
        # Registers the commands for controlling the power supply
        return {
            'PS_SETUP_VOLTAGE': self.power_supply.setup_voltage,
            'PS_SETUP_CURRENT': self.power_supply.setup_current,
            'PS_POWER_ON': self.power_supply.power_on,
            'PS_POWER_OFF': self.power_supply.power_off
        }

    # Additional methods for handling communication with the power supply
    # For example:
    def setup_voltage(self, voltage, channel):
        # Logic to set the voltage
        pass

    def setup_current(self, current, channel):
        # Logic to set the current
        pass

    def power_on(self):
        # Logic to power on the device
        pass

    def power_off(self):
        # Logic to power off the device
        pass



