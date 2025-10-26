# DEPRECATED CONSTANTS - Use new constants below instead
import warnings

# Deprecated constants with warnings
def _deprecated_constant(old_name, new_name):
    warnings.warn(
        f"{old_name} is deprecated. Use {new_name} instead.",
        DeprecationWarning,
        stacklevel=3
    )

NEASMART_SYSBUS_BAUD = 38400
NEASMART_SYSBUS_DATA_BITS = 8
NEASMART_SYSBUS_STOP_BITS = 1
NEASMART_SYSBUS_PARITY = "N"

# Deprecated - use ZONE_BASE_ID_MULTIPLIER instead
NEASMART_BASE_SLAVE_ADDR = 1200
def get_NEASMART_BASE_SLAVE_ADDR():
    _deprecated_constant("NEASMART_BASE_SLAVE_ADDR", "ZONE_BASE_ID_MULTIPLIER")
    return NEASMART_BASE_SLAVE_ADDR

# Deprecated - use ZONE_ID_MULTIPLIER instead  
BASE_ZONE_ID = 100
def get_BASE_ZONE_ID():
    _deprecated_constant("BASE_ZONE_ID", "ZONE_ID_MULTIPLIER")
    return BASE_ZONE_ID

ZONE_SETPOINT_ADDR_OFFSET = 1
ZONE_TEMP_ADDR_OFFSET = 2
ZONE_RH_ADDR_OFFSET = 10
MIXEDGROUP_BASE_REG = {
    1: 10,
    2: 14,
    3: 18,
}
MIXEDGROUP_VALVE_OPENING_OFFSET = 0
MIXEDGROUP_PUMP_STATE_OFFSET = 1
MIXEDGROUP_FLOW_TEMP_OFFSET = 2
MIXEDGROUP_RETURN_TEMP_OFFSET = 3
OUTSIDE_TEMPERATURE_ADDR = 7
FILTERED_OUTSIDE_TEMPERATURE_ADDR = 8
HINTS_PRESENT_ADDR = 6
WARNINGS_PRESENT_ADDR = 5
ERRORS_PRESENT_ADDR = 3
GLOBAL_OP_MODE_ADDR = 1
GLOBAL_OP_STATE_ADDR = 2
DEHUMIDIFIERS_ADDR_OFFSET = 21
EXTRA_PUMPS_ADDR_OFFSET = 30
READ_HR_CODE = 3
WRITE_HR_CODE = 6

# Deprecated - use OUTSIDE_TEMPERATURE_ADDR instead
OUTSIDE_TEMP_REG = 7
def get_OUTSIDE_TEMP_REG():
    _deprecated_constant("OUTSIDE_TEMP_REG", "OUTSIDE_TEMPERATURE_ADDR")
    return OUTSIDE_TEMP_REG

# Deprecated - use FILTERED_OUTSIDE_TEMPERATURE_ADDR instead
FILTERED_OUTSIDE_TEMP_REG = 8
def get_FILTERED_OUTSIDE_TEMP_REG():
    _deprecated_constant("FILTERED_OUTSIDE_TEMP_REG", "FILTERED_OUTSIDE_TEMPERATURE_ADDR")
    return FILTERED_OUTSIDE_TEMP_REG

SQLITEDICT_REGS_TABLE = "holding_registers"
REGS_STARTING_ADDR = 0
DATASTORE_PATH = "./data/registers.db"


## new constants


# Modbus communication parameters (from Rehau NEA SMART 2.0 documentation)

# Serial communication parameters for SYSBUS interface (Modbus RTU over RS-485)
NEASMART_SYSBUS_BAUD = 38400             # Baud rate: 38400 bits/s (see page 12 of the manual)
NEASMART_SYSBUS_DATA_BITS = 8            # 8 data bits per message (default standard)
NEASMART_SYSBUS_STOP_BITS = 1            # 1 stop bit used (specified as "Nessuno (1 bit di stop)")
NEASMART_SYSBUS_PARITY = "N"             # No parity bit used

# Modbus slave addresses used by the NEA SMART 2.0 system
NEASMART_SLAVE_ADDRESS_PRIMARY = 240     # Main slave address (page 12)
NEASMART_SLAVE_ADDRESS_SECONDARY = 241   # Secondary address if present

# Data representation
NEASMART_BYTE_ORDER = "MSB"              # Byte order: Most Significant Byte first (MSB-first)
NEASMART_REGISTER_START = 0              # First register address starts at 0

# Base addressing for local zones and slave addressing
ZONE_BASE_ID_MULTIPLIER = 1200           # Multiplier for the base ID in address calculation.
ZONE_ID_MULTIPLIER = 100                 # Multiplier for the zone ID in address calculation.
ZONE_SETPOINT_ADDR_OFFSET = 1            # Offset for temperature setpoint (YY01)
ZONE_TEMP_ADDR_OFFSET = 2                # Offset for actual temperature (YY02)
ZONE_RH_ADDR_OFFSET = 10                 # Offset for relative humidity (YY10, optional)

# Base register addresses for mixed circuits (page 16)
MIXEDGROUP_BASE_REG = {
    1: 10,     # MIXG1 base register
    2: 14,     # MIXG2 base register
    3: 18,     # MIXG3 base register
}

# Offsets for values within each mixed circuit group
MIXEDGROUP_VALVE_OPENING_OFFSET = 0      # Mixing valve opening [%] (Low byte, DPT 05)
MIXEDGROUP_PUMP_STATE_OFFSET = 1         # Pump state [0/1] (bitwise in word register)
MIXEDGROUP_FLOW_TEMP_OFFSET = 2          # Flow temperature [°C or F] (High/Low byte, DPT 07)
MIXEDGROUP_RETURN_TEMP_OFFSET = 3        # Return temperature [°C or F] (High/Low byte, DPT 07)

# External/global readings and status flags (page 14)
OUTSIDE_TEMPERATURE_ADDR = 7             # Outside temperature (High/Low byte)
FILTERED_OUTSIDE_TEMPERATURE_ADDR = 8    # Filtered outside temperature (High/Low byte)
HINTS_PRESENT_ADDR = 6                   # Hints flag (bit 00 in word register)
WARNINGS_PRESENT_ADDR = 5                # Warnings present flag (bit 00)
ERRORS_PRESENT_ADDR = 3                  # Errors present flag (bit 00)

# Global operation
GLOBAL_OP_MODE_ADDR = 1                  # Operating mode (Auto, Heat, Cool...) page 14:
                                        #   1 = Auto
                                        #   2 = Heating
                                        #   3 = Cooling
                                        #   4 = Manual heating
                                        #   5 = Manual cooling

GLOBAL_OP_STATE_ADDR = 2                 # Global state of operation (page 14):
                                        #   1 = Normal operation
                                        #   2 = Reduced
                                        #   3 = Standby
                                        #   4 = Scheduled
                                        #   5 = Party
                                        #   6 = Holiday/Absent

# Other device types and special equipment
DEHUMIDIFIERS_ADDR_OFFSET = 21           # Starting Modbus ID offset for up to 9 dehumidifiers (IDs 22-30)
EXTRA_PUMPS_ADDR_OFFSET = 30             # Starting offset for 5 extra pumps (IDs 31-35)

# Modbus function codes for interaction
READ_HR_CODE = 3                         # Function code 03: Read Holding Register
WRITE_HR_CODE = 6                        # Function code 06: Write Single Register

# Local SQLite and JSON file paths
SQLITEDICT_REGS_TABLE = "holding_registers"  # Table name in local SQLite DB
REGS_STARTING_ADDR = 0                        # Base register address for SQLite mapping
DATASTORE_PATH = "./data/registers.db"        # Path to local DB for register storage

# Global operation status mapping (more intuitive for global operation)
GLOBAL_OP_STATUS_MAPPING = {
    0: "off",
    1: "presence",      # Zone is active and occupied
    2: "away",          # Zone is in energy-saving mode
    3: "standby",       # Zone is in standby
    4: "scheduled",     # Zone follows a schedule
    5: "party",         # Zone is in party mode
    6: "holiday"        # Zone is in long-term away mode
}
ZONE_OP_STATUS_MAPPING = {v: k for k, v in GLOBAL_OP_STATUS_MAPPING.items()}


# Global operation status mapping (more intuitive for global operation)
ZONE_OP_STATUS_MAPPING = {
    0: "off",
    1: "presence",      # Zone is active and occupied
    2: "away",          # Zone is in energy-saving mode
    3: "standby",       # Zone is in standby
    4: "scheduled",     # Zone follows a schedule
}
ZONE_OP_STATUS_MAPPING = {v: k for k, v in ZONE_OP_STATUS_MAPPING.items()}

GLOBAL_OP_MODE_MAPPING = {
    0: "off",
    1: "auto",
    2: "heating",
    3: "cooling",
    4: "manual heating",
    5: "manual cooling"
}
GLOBAL_OP_MODE_MAPPING_REVERSE = {v: k for k, v in GLOBAL_OP_MODE_MAPPING.items()}