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
            if error == ERROR.ERROR_OK:
                print("TX  {}".format(frames[n]))
            else:
                print("TX failed with error code {}".format(error))


        # keep both delays same in order to avoid delay of one task over another
        yield [pyRTOS.delay(1)]


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
            print(str(iframe))
            if (str(iframe) == "       1   [8]  01 00 00 00 00 00 00 00"):
                relay_pin.on()
            if (str(iframe) == "       1   [8]  00 00 00 00 00 00 00 00"):
                relay_pin.off()

        # keep both delays same in order to avoid delay of one task over another
        yield [pyRTOS.delay(1)]


# Add task in core of pyRTOS and set tasks properties
pyRTOS.add_task(pyRTOS.Task(task_1, priority=1, name="task_1"))
pyRTOS.add_task(pyRTOS.Task(task_2, priority=1, name="task_2"))

# Start pyRTOS
pyRTOS.start()


