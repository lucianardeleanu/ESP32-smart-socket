"""Main Module of Entire script
    @TODO None
"""

__author__ = "Ardeleanu Lucian"
__copyright__ = "Copyright 2021"
__credits__ = ["None"]
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "lucian.ardeleanu@autoliv.com"
__status__ = "In-Work"


# -------------------------- IMPORTS ------------------------------
import time
import math
import pyRTOS
import ACS_712_Current_Sensor
import ZMPT101B_Voltage_Sensor

from mcp2515_can_lib import (
    CAN,
    CAN_CLOCK,
    CAN_EFF_FLAG,
    CAN_ERR_FLAG,
    CAN_RTR_FLAG,
    CAN_SPEED,
    ERROR,
)
from mcp2515_can_lib import SPIESP32 as SPI
from mcp2515_can_lib import CANFrame
import dht
import machine
from machine import Pin
from machine import ADC

# -------------------- GLOBAL INITIALISATIONS ---------------------

# print a message before starting initialisation
print("===================================================")
print("        --------------------------------           ")
print("        | ESP32 SMART PLUG IOT PROJECT |           ")
print("        --------------------------------           ")
print("   Author: Ardeleanu Lucian                        ")
print(' DO NOT CONNECT NOTHING IN PLUG WHILE CALIBRATING! ')
print("===================================================")

# ---------- CAN Initialisation -----------
can = CAN(SPI(cs=27))

# Configuration
if can.reset() != ERROR.ERROR_OK:
    print("Can not reset for MCP2515")

if can.setBitrate(CAN_SPEED.CAN_125KBPS, CAN_CLOCK.MCP_8MHZ) != ERROR.ERROR_OK:
    print("Can not set bitrate for MCP2515")

if can.setNormalMode() != ERROR.ERROR_OK:
    print("Can not set normal mode for MCP2515")

# Keeps a small delay between inits
time.sleep(1)

# ----------- Relay Initialisation ----------
Relay_Status = Pin(22, Pin.OUT)

# Keeps a small delay between inits
time.sleep(1)

# ----- Current Sensor Initialisation -------
# Force relay to stay on
Relay_Status.on()

# Call Calibration Function
Calculated_AC_Current_In_Calibraton = ACS_712_Current_Sensor.Calibrate_Current_Sensor_ACS_712()

# Define global value of measured current ( in Amps)
Calculated_AC_Current = 0

# Keeps a small delay between inits
time.sleep(2)

# ----- Voltage Sensor Initialisation -------
# Force relay to stay off
Relay_Status.off()

# Keeps a small delay between inits
time.sleep(2)

# Call Calibration Function
Voltage_Sensor_Zero_Point_Calibration = ZMPT101B_Voltage_Sensor.Calibrate_Voltage_Sensor_ZMPT101B()

# Define global value of measured voltage ( in Volts )
Calculated_AC_Voltage = 0

# Keeps a small delay between inits
time.sleep(2)

# ----- Humidity Sensor Initialisation -------
# Define sensor object
dht_sensor_object = dht.DHT11(machine.Pin(4))

# Define sensor measured humidity
Measured_Humidity = 0

# print a message after initialisation
print('Initialisation Finished!')


# Function used to convert a float value to a bytes-frame value
def convert_float_to_can_frame(float_value):

    # Define frame
    frame = bytearray()

    # Check if . in string
    if '.' in str(float_value):

        # Split by .
        values_string_list = str(float_value).split('.')

        # Extract values from list
        if len(values_string_list) == 2:
            integer_part = int(values_string_list[0])
            decimal_part = int(values_string_list[1])
        else:
            integer_part = 0
            decimal_part = 0

        # Construct frame
        frame.append(0x00)
        frame.append(0x00)
        frame.append(0x00)
        frame.append(0x00)
        frame.append(0x00)
        frame.append(0x00)
        frame.append(integer_part)
        frame.append(decimal_part)

    else:
        # Construct frame
        frame.append(0x00)
        frame.append(0x00)
        frame.append(0x00)
        frame.append(0x00)
        frame.append(0x00)
        frame.append(0x00)
        frame.append(0x00)
        frame.append(float_value)

    # Return frame
    return frame

# =========================================================
#              DEFINE TASK OF PYRTOS
# Task needed TRANSMITING FRAMES WITH DATA OVER CAN
# =========================================================
def task_1(self):

    # Point to global value
    global can
    global Calculated_AC_Voltage
    global Calculated_AC_Current
    global Measured_Humidity

    while True:

        # Receive messages from other tasks
        msgs = self.recv()
        for msg in msgs:

            # If data has arrived from other 2 tasks, then let's process it
            print('------------------------')

            if msg.type == 130:
                # -------------- SEND VOLTAGE FRAME ------------------------------
                # Convert to bytes
                voltage_bytes = convert_float_to_can_frame(Calculated_AC_Voltage)

                # Construct frame
                voltage_frame = CANFrame(can_id=0x01, data=voltage_bytes)

                # Send frame
                error = can.sendMessage(voltage_frame)

                # -------------- SEND CURRENT FRAME ------------------------------
                # Convert to bytes
                current_bytes = convert_float_to_can_frame(Calculated_AC_Current)

                # Construct frame
                current_frame = CANFrame(can_id=0x02, data=current_bytes)

                # Send frame
                error = can.sendMessage(current_frame)

                # -------------- SEND POWER FRAME ------------------------------
                # Calculate power
                Calculated_Electric_Power = Calculated_AC_Current * Calculated_AC_Voltage

                # Convert to bytes
                Power_bytes = convert_float_to_can_frame(Calculated_Electric_Power)

                # Construct frame
                Power_frame = CANFrame(can_id=0x03, data=Power_bytes)

                # Send frame
                error = can.sendMessage(Power_frame)

                print('DATA FROM TASK 3:')
                print('Measured Voltage:', Calculated_AC_Voltage)
                print('Measured Current:', Calculated_AC_Current)
                print('Measured Power:', Calculated_Electric_Power)

            if msg.type == 135:
                # -------------- SEND Humidity FRAME ------------------------------
                # Convert to bytes
                Humidity_bytes = convert_float_to_can_frame(Measured_Humidity)

                # Construct frame
                Humidity_frame = CANFrame(can_id=0x04, data=Humidity_bytes)

                # Send frame
                error = can.sendMessage(Humidity_frame)

                print('DATA FROM TASK 2:')
                print('Measured Humidity:', Measured_Humidity)

        print('------------------------')


        # Wait until message arrives from other tasks
        yield [pyRTOS.wait_for_message(self)]



# =========================================================
#              DEFINE TASK OF PYRTOS
# Task needed for actuating relay and humidity receive
# Power Supply: 3.3V
# Output Pin: D22
# =========================================================
def task_2(self):

    # Point to global value
    global can

    # Point to global values
    global Relay_Status
    global Measured_Humidity
    global dht_sensor_object

    # Set ready message for task_2
    ready_message = 135

    # ---------------------- Infinite Cicle -----------------------------
    while True:

        # Measure humidity
        dht_sensor_object.measure()
        Measured_Humidity = dht_sensor_object.humidity()

        # Send ready message to task 1
        self.send(pyRTOS.Message(ready_message, self, "task_1"))

        # Call function to read CAN Message Buffer
        error, iframe = can.readMessage()

        # If message arrived and it's ok
        if (Measured_Humidity < 75 ):

            if error == ERROR.ERROR_OK:

                if (str(iframe) == "       1   [8]  01 00 00 00 00 00 00 00" ):
                    # Set Relay ON
                    Relay_Status.on()

                if (str(iframe) == "       1   [8]  00 00 00 00 00 00 00 00" ):

                    # Set Relay OFF
                    Relay_Status.off()
        else:
            # Set Relay OFF
            Relay_Status.off()

        # keep both delays same in order to avoid delay of one task over another
        yield [pyRTOS.delay(20)]


# ==========================================================================
#              DEFINE TASK OF PYRTOS
# Task needed for reading Current Sensor ACS712 and Voltage Sensor ZMPT101B
# Power Supply: 5V ( Vin PIN )
# Output Pin: D32 - Current Sensor ACS712
# Output Pin: D33 - Voltage Sensor ZMPT101B
# ==========================================================================
def task_3(self):

    # Point to global value
    global Calculated_AC_Current

    # Point to global value
    global Calculated_AC_Voltage

    # Set a ready message for task_3
    ready_message = 130

    # ---------------------- Infinite Cicle -----------------------------
    while True:

        # Get Current from sensor
        Calculated_AC_Current = ACS_712_Current_Sensor.Get_Value_From_Current_Sensor_ACS_712( Calculated_AC_Current_In_Calibraton )

        # Get Voltage from sensor
        Calculated_AC_Voltage = ZMPT101B_Voltage_Sensor.Get_Value_From_Voltage_Sensor_ZMPT101B( Voltage_Sensor_Zero_Point_Calibration )

        # Send ready message to task 1
        self.send(pyRTOS.Message(ready_message, self, "task_1"))

        # keep both delays same in order to avoid delay of one task over another
        yield [pyRTOS.delay(10)]


# ================ CALL TASKS IN PYRTOS ENGINE ======================
pyRTOS.add_task(pyRTOS.Task(task_1, priority=1, name="task_1", mailbox=True))
pyRTOS.add_task(pyRTOS.Task(task_2, priority=1, name="task_2", mailbox=True))
pyRTOS.add_task(pyRTOS.Task(task_3, priority=1, name="task_3", mailbox=True))


# Start pyRTOS
pyRTOS.start()


