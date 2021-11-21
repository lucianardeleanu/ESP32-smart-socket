"""ACS 712 Current Sensor Library
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

# -------------------- ADC INITIALISATION --------------------------
# create ADC object on ADC pin
adc_1 = ADC(Pin(32))

# 0dB attenuation, gives a maximum input voltage of 1.00v - this is the default configuration
adc_1.atten(ADC.ATTN_11DB)

# 12 bit data - this is the default configuration
adc_1.width(ADC.WIDTH_12BIT)

# Define ADC Scale
Adc_Current_Sensor_Scale = 4095

# Define ADC Reference Voltage
ADC_Current_Sensor_Reference = 5

# --------------------- CONVERSION PARAMETERS -----------------------
# Define a number of samples per calibration
Current_Sensor_Calibration_Samples = 100

# Define current sensor sensitivity in V/A
AC_Current_Sensor_Sensitivity = 0.100

# Define current sensor middle value
AC_Current_Sensor_Middle_Value = 2.45

# =========================================================
#   FUNCTION NEEDED FOR SENSOR CALIBRATION
#   Description:
#       This function must be called once in init zone.
#       CALL THIS FUNCTION WITH SENSOR POWERED AND A CURRENT
#       OF 0 AMPS
#   Parameters In:  NONE
#   Parameters Out: Value of offset current ( in Amps )
# =========================================================
def Calibrate_Current_Sensor_ACS_712():

    # --------------------- SENSOR CALIBRATION --------------------------
    # Define a sum of readings from ADC
    Sum_of_readings_from_ADC = 0

    # Aquire a number of samples in a sum buffer
    for i in range(0, Current_Sensor_Calibration_Samples):
        # Aquire Value
        Sum_of_readings_from_ADC += adc_1.read()

    # Calculate the zero point of calibration
    Current_Sensor_Zero_Point_Calibration = Sum_of_readings_from_ADC / Current_Sensor_Calibration_Samples

    # Calculate voltage over sensor in calibration
    Current_Sensor_Output_Voltage_In_Calibration = Current_Sensor_Zero_Point_Calibration * ( ADC_Current_Sensor_Reference / Adc_Current_Sensor_Scale )

    # Calculate Current from upper voltage
    Calculated_AC_Current_In_Calibraton = ( Current_Sensor_Output_Voltage_In_Calibration - AC_Current_Sensor_Middle_Value ) / AC_Current_Sensor_Sensitivity

    # Return current value in amps
    return Calculated_AC_Current_In_Calibraton

# =========================================================
#   FUNCTION NEEDED FOR SENSOR READINGS
#   Description:
#       This function can be called multiple times.
#       This function return readed current in amps.
#   Parameters In:  Current from calibration function
#   Parameters Out: Value of readed current ( in Amps )
# =========================================================
def Get_Value_From_Current_Sensor_ACS_712( Calculated_AC_Current_In_Calibraton ):

    # ---------------------- Infinite Cicle -----------------------------
    # Define a sum of readings from ADC
    Sum_of_readings_from_ADC = 0

    # Define a number of aquisitions
    Number_Of_Aquisitions = 0

    for Counter_For_Number_Of_Samples in range(0, Current_Sensor_Calibration_Samples):
        # Instataneous read from ADC
        ADC_Current_Sensor_Reading = adc_1.read()

        # Add Readings to sum
        Sum_of_readings_from_ADC += ADC_Current_Sensor_Reading * ADC_Current_Sensor_Reading

        # Increment number of aquisitions
        Number_Of_Aquisitions += 1

    # Calculate output of current sensor in volts
    Current_Sensor_Output_Voltage = math.sqrt(Sum_of_readings_from_ADC / Number_Of_Aquisitions) * ( ADC_Current_Sensor_Reference / Adc_Current_Sensor_Scale)

    # Calculate AC Current from upper calculated voltage
    Calculated_absolute_AC_Current = ( Current_Sensor_Output_Voltage - AC_Current_Sensor_Middle_Value) / AC_Current_Sensor_Sensitivity

    # Calculate AC Current
    Calculated_AC_Current = abs(Calculated_absolute_AC_Current - Calculated_AC_Current_In_Calibraton)

    # Round at only 2 decimals
    Calculated_AC_Current = round(Calculated_AC_Current, 2)

    # Return calculated current
    return Calculated_AC_Current