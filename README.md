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

The possibility of controlling the smart socket through the Raspberry Pi 3b + development board has been added, the board containing a CAN MCP2515 interface and a 5 "touch screen display attached.
Thus, a Python application was created and was configured to launch when the development board is also powered.
The created application has the possibility to read the voltage, current, power and humidity on the CAN communication line and to activate and deactivate the smart socket.
The created application can only be run on Raspbian OS, so it is not currently optimized to work on Windows.

![2022-01-02-134704_800x600_scrot](https://user-images.githubusercontent.com/72782466/148778449-93b8be39-4963-483f-a3ec-b4599de5623b.png)

In terms of real-time requirements, it was necessary to implement a method of signaling the priority of tasks. As can be seen in the main.py file, all functions have the same running priority, but in order to avoid data collision, certain mechanisms have been created.

The created tasks have the following main roles:

1. The data to be used in all tasks will be set in global variables, so it will be possible to find in global variables the value of voltage, current and humidity;
2. Task number 3 will be responsible for calculating current and voltage;
3. Task number 2 will be responsible for measuring humidity and activating / deactivating the system relay, as appropriate.
4. Task number 1 will be responsible for sending the data on the CAN communication protocol.


Task 1 will wait until you receive a message (signal) from the other 2 tasks. If a READY signal has been received, then the received data will be processed and sent to the CAN communication protocol.
For uniform execution, it has been decided that task 3 should be executed at an interval of 10 clock cycles, task 2 should be executed at an interval of 20 clock cycles, and task 1 should be executed when a message was received from one of the two tasks. Thus, pyRTOS provides a buffer in which messages will be stored, a buffer that is automatically deleted after receiving them.
