"""ZMPT101B Voltage Sensor Library
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
from machine import ADC
from machine import Pin
import math
import time

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

# =========================================================
#   FUNCTION NEEDED FOR SENSOR CALIBRATION
#   Description:
#       This function must be called once in init zone.
#       CALL THIS FUNCTION WITH SENSOR POWERED AND A VOLTAGE
#       OF 0 VOLTS
#   Parameters In:  NONE
#   Parameters Out: OFFSET OF VOLTAGE SENSOR
# =========================================================

def Calibrate_Voltage_Sensor_ZMPT101B():

    # --------------------- SENSOR CALIBRATION --------------------------
    # Define a sum of readings from ADC
    Sum_of_readings_from_ADC = 0

    # Define a number of samples per calibration
    Number_of_calibration_samples = 10

    # Aquire a number of samples in a sum buffer
    for i in range(0,Number_of_calibration_samples):

        # Aquire signal from ADC
        Sum_of_readings_from_ADC += adc_2.read()

    # Calculate the zero point of calibration
    Voltage_Sensor_Zero_Point_Calibration = Sum_of_readings_from_ADC / Number_of_calibration_samples

    # Return offset of voltage sensor
    return Voltage_Sensor_Zero_Point_Calibration


# =========================================================
#   FUNCTION NEEDED FOR SENSOR READINGS
#   Description:
#       This function can be called multiple times.
#       This function return readed voltage in Volts.
#   Parameters In:  Voltage_Sensor_Zero_Point_Calibration
#   Parameters Out: Value of readed voltage ( in Volts )
# =========================================================
def Get_Value_From_Voltage_Sensor_ZMPT101B( Voltage_Sensor_Zero_Point_Calibration ):

    # Calculate AC Voltage Period
    AC_Voltage_Period = 1000000 / AC_Voltage_Frequency

    # Get start time of data aquisition
    start_time_of_aquisition = time.ticks_us()

    # Define a sum of readings from ADC
    Sum_of_readings_from_ADC = 0

    # Define a number of aquisitions
    Number_Of_Aquisitions = 0

    while (time.ticks_us() - start_time_of_aquisition < AC_Voltage_Period):
        # Instataneous read from ADC
        ADC_voltage_sensor_reading = adc_2.read() - Voltage_Sensor_Zero_Point_Calibration

        # Add Readings to sum
        Sum_of_readings_from_ADC += ADC_voltage_sensor_reading * ADC_voltage_sensor_reading

        # Increment number of aquisitions
        Number_Of_Aquisitions += 1

    # Calculate AC Voltage
    Calculated_AC_Voltage = math.sqrt( Sum_of_readings_from_ADC / Number_Of_Aquisitions) / Adc_voltage_sensor_scale * ADC_Voltage_Sensor_Reference / AC_Voltage_Sensor_Sensitivity

    # Round at only 2 decimals
    Calculated_AC_Voltage = round(Calculated_AC_Voltage, 2)

    # Return calculated value
    return Calculated_AC_Voltage