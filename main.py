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


# ============ IMPORTS ==================
import time
import math
import pyRTOS

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

from machine import Pin
from machine import ADC
# =======================================

# =========================================================
# INIT GLOBAL FUNCTION AND VARIABLES
# =========================================================

def CAN_Init():
    # Initialization
    can = CAN(SPI(cs=23))

    # Configuration
    if can.reset() != ERROR.ERROR_OK:
        print("Can not reset for MCP2515")
        return 1
    if can.setBitrate(CAN_SPEED.CAN_125KBPS, CAN_CLOCK.MCP_8MHZ) != ERROR.ERROR_OK:
        print("Can not set bitrate for MCP2515")
        return 1
    if can.setNormalMode() != ERROR.ERROR_OK:
        print("Can not set normal mode for MCP2515")
        return 1

    return can

# =========================================================


# =========================================================
# DEFINE FIRST TASK OF PYRTOS
# =========================================================
def task_1(self):

    can = CAN_Init()

    # Prepare frames
    data = b"\x12\x34\x56\x78\x9A\xBC\xDE\xF0"  # type: bytes
    sff_frame = CANFrame(can_id=0x7FF, data=data)
    sff_none_data_frame = CANFrame(can_id=0x7FF)
    err_frame = CANFrame(can_id=0x7FF | CAN_ERR_FLAG, data=data)
    eff_frame = CANFrame(can_id=0x12345678 | CAN_EFF_FLAG, data=data)
    eff_none_data_frame = CANFrame(can_id=0x12345678 | CAN_EFF_FLAG)
    rtr_frame = CANFrame(can_id=0x7FF | CAN_RTR_FLAG)
    rtr_with_eid_frame = CANFrame(can_id=0x12345678 | CAN_RTR_FLAG | CAN_EFF_FLAG)
    rtr_with_data_frame = CANFrame(can_id=0x7FF | CAN_RTR_FLAG, data=data)
    frames = [
        sff_frame,
        sff_none_data_frame,
        err_frame,
        eff_frame,
        eff_none_data_frame,
        rtr_frame,
        rtr_with_eid_frame,
        rtr_with_data_frame,
    ]

    # Read all the time and send message in each second
    end_time, n = time.ticks_add(time.ticks_ms(), 1000), -1  # type: ignore
    while True:
        # error, iframe = can.readMessage()
        # if error == ERROR.ERROR_OK:
        #     #print("RX  {}".format(iframe))
        #     rx_frame = iframe

        if time.ticks_diff(time.ticks_ms(), end_time) >= 0:  # type: ignore
            end_time = time.ticks_add(time.ticks_ms(), 1000)  # type: ignore
            n += 1
            n %= len(frames)

            error = can.sendMessage(frames[n])
            # if error == ERROR.ERROR_OK:
            #     print("TX  {}".format(frames[n]))
            # else:
            #     print("TX failed with error code {}".format(error))


        # keep both delays same in order to avoid delay of one task over another
        yield [pyRTOS.delay(10)]


# =========================================================
# DEFINE SECOND TASK OF PYRTOS
# =========================================================
def task_2(self):

    can = CAN_Init()

    # Init replay pin
    relay_pin = Pin(15, Pin.OUT)

    # Infinite Cicle
    while True:

        error, iframe = can.readMessage()
        if error == ERROR.ERROR_OK:
            # print(str(iframe))
            if (str(iframe) == "       1   [8]  01 00 00 00 00 00 00 00"):
                relay_pin.on()
            if (str(iframe) == "       1   [8]  00 00 00 00 00 00 00 00"):
                relay_pin.off()

        # keep both delays same in order to avoid delay of one task over another
        yield [pyRTOS.delay(1)]

# =========================================================
# DEFINE THIRD TASK OF PYRTOS
# =========================================================
def task_3(self):

    adc = ADC(Pin(32))  # create ADC object on ADC pin
    adc.atten(ADC.ATTN_11DB)  # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
    adc.width(ADC.WIDTH_12BIT)  # set 9 bit return values (returned range 0-4095)

    # Current sensor sensitivity in V/A
    current_sensor_sensitivity = 0.100

    # Define ADC Range
    ADC_Range = 4095

    # Infinite Cicle
    while True:

        # Read from ADC
        ADC_reading = adc.read()

        # Read sensor output
        sensor_output = ADC_reading * ( 3.3 / ADC_Range)

        # print("Sensor output: " + str(sensor_output) )

        # Calculate readed current
        calculated_current = ( sensor_output - 2.45 ) / current_sensor_sensitivity

        # print("calculated_current: " + str(calculated_current))


        # keep both delays same in order to avoid delay of one task over another
        yield [pyRTOS.delay(100)]



# =========================================================
#              DEFINE THIRD TASK OF PYRTOS
# Task needed for reading Voltage Sensor ZMPT101B
# Power Supply: 5V ( Vin PIN )
# Output Pin: D33
# =========================================================
def task_4(self):

    # -------------------- ADC INITIALISATION --------------------------
    # create ADC object on ADC pin
    adc_2 = ADC(Pin(33))

    # 0dB attenuation, gives a maximum input voltage of 1.00v - this is the default configuration
    adc_2.atten(ADC.ATTN_0DB)

    # 12 bit data - this is the default configuration
    adc_2.width(ADC.WIDTH_12BIT)

    # Define ADC Scale
    Adc_voltage_sensor_scale = 4095

    # Define ADC Reference Voltage
    ADC_Voltage_Sensor_Reference = 5

    # --------------------- CONVERSION PARAMETERS -----------------------
    # Define AC Voltage Frequency
    AC_Voltage_Frequency = 50

    # Define sensor sensitivity
    AC_Voltage_Sensor_Sensitivity = 0.0050

    # --------------------- SENSOR CALIBRATION --------------------------
    # Define a sum of readings from ADC
    Sum_of_readings_from_ADC = 0

    # Define a number of samples per calibration
    Number_of_calibration_samples = 10

    # Aquire a number of samples in a sum buffer
    for i in range(0,Number_of_calibration_samples):
        Sum_of_readings_from_ADC += adc_2.read()

    # Calculate the zero point of calibration
    Voltage_Sensor_Zero_Point_Calibration = Sum_of_readings_from_ADC / Number_of_calibration_samples


    # ---------------------- Infinite Cicle -----------------------------
    while True:

        # Calculate AC Voltage Period
        AC_Voltage_Period = 1000000 / AC_Voltage_Frequency

        # Get start time of data aquisition
        start_time_of_aquisition = time.ticks_us()

        # Define a sum of readings from ADC
        Sum_of_readings_from_ADC = 0

        # Define a number of aquisitions
        Number_Of_Aquisitions = 0

        while (time.ticks_us() - start_time_of_aquisition < AC_Voltage_Period ):

            # Instataneous read from ADC
            ADC_voltage_sensor_reading = adc_2.read() - Voltage_Sensor_Zero_Point_Calibration

            # Add Readings to sum
            Sum_of_readings_from_ADC += ADC_voltage_sensor_reading * ADC_voltage_sensor_reading

            # Increment number of aquisitions
            Number_Of_Aquisitions += 1

        # Calculate AC Voltage
        Calculated_AC_Voltage =  math.sqrt(Sum_of_readings_from_ADC / Number_Of_Aquisitions  ) / Adc_voltage_sensor_scale * ADC_Voltage_Sensor_Reference / AC_Voltage_Sensor_Sensitivity

        print("Calculated voltage:", Calculated_AC_Voltage )

        # keep both delays same in order to avoid delay of one task over another
        yield [pyRTOS.delay(1)]


# Add task in core of pyRTOS and set tasks properties
# pyRTOS.add_task(pyRTOS.Task(task_1, priority=1, name="task_1"))
pyRTOS.add_task(pyRTOS.Task(task_2, priority=1, name="task_2"))
pyRTOS.add_task(pyRTOS.Task(task_3, priority=1, name="task_3"))
pyRTOS.add_task(pyRTOS.Task(task_4, priority=1, name="task_4"))


# Start pyRTOS
pyRTOS.start()


