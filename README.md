# ESP32-smart-socket
A Smart Socket implementation using Micropython on ESP32 microcontroller. 

This Device will communicate over CAN Communication Protocol and will react when specific frames are sended over it.

The device created is based on the ESP32 development board programmed with the Micropython programming language. Thus, with the help of the PyRTOS real-time operating system, several tasks have been created that will run in parallel, each task having a well-defined role in the case of this project.
The project has in its composition the following modules:
1. MCP2515 SPI TO CAN module used to control the smart socket via the CAN communication protocol;
2. 5V Relay Actuator Module used in opening and closing the smart socket;
3. DHT11 Humidity and Temperature Sensor module used in measuring the humidity of the outlet and the automatic shutdown of the smart outlet in case the humidity increases above a certain level;
4. ACS712 current sensor module used to measure the current that will pass through the intelligent socket;
5. ZMPT101B voltage sensor module used to measure voltage drop on smart socket;
6. ESP32 development board.

Thus, through CAN communication, when transmitting certain frames, it is possible to order the intelligent socket to execute the following:
1. To stop or start by means of the relay the flow of voltage and current through the socket;
2. To return the value of the electric power (through the product Current * Voltage);
3. To return the value of the voltage drop on the smart socket;
4. To return the value of the current through the intelligent socket;
5. To return the humidity value of the smart socket;
