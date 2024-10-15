# R307 Fingerprint Sensor Module with FTDI232

This repository provides a C-based library for interfacing the **R307 Fingerprint Sensor Module** using the **FTDI232 USB-to-UART bridge**. The library supports key functionalities for communicating with the sensor and handling fingerprint data using the FTDI232 for serial communication.

## Features
- Interface with R307 Fingerprint Sensor using FTDI232 via UART.
- Supports standard UART communication (57600 baud, 8 data bits, 1 stop bit, no parity).
- Implements checksum validation, command parsing, and sensor response handling.
- Currently supports 22 functions as per the R307 module's user manual, including enrolling, verifying, and reading fingerprint data.
- Modifiable module address and password functionality.
- Extensible for additional R307 commands in the future (e.g., Notepad functions).

## Requirements
- **R307 Fingerprint Sensor Module**  
- **FTDI232 USB-to-UART bridge**
- **PC or microcontroller with USB support**

### Hardware Connection

The connection diagram below shows how to wire the R307 module to the FTDI232 module:

![image alt](image_https://github.com/SunilGargg/R307-Fingerprint-Sensor-on-FTDI232/blob/8a4feae34df54840cbf2fe9fc2ec143ce59b996d/Add%20a%20subheading.png)

| **FTDI232**  | **R307 Fingerprint Sensor** |
|--------------|-----------------------------|
| VCC (3.3V)   | Pin 1 (VCC)                 |
| GND          | Pin 2 (GND)                 |
| TXD          | Pin 3 (TXD)                 |
| RXD          | Pin 4 (RXD)                 |
| Not Connected| Pin 5 (NC)                  |
| Not Connected| Pin 6 (NC)                  |

The **FTDI232** converts USB signals from the host system (e.g., a PC or a microcontroller with USB support) to UART, enabling communication between the host system and the R307 sensor.

## Software Flow

The software library is built to manage communication between the FTDI232 and the R307 module over UART. The primary functions provided by the library include initialization, checksum calculation, command/response handling, and data parsing.

### Key Functions

1. **`r307_init()`**  
   Initializes the FTDI232 UART interface with a baud rate of 57600. The function configures UART parameters (8 data bits, 1 stop bit, no parity) and prepares the communication with the R307 sensor.

2. **`check_sum()`**  
   Performs a checksum calculation (modulo 256) for the R307 packets. The checksum is calculated over the package identifier, package length, instruction code, and packet data if present (e.g., new module address, password).

3. **`r307_response()`**  
   Handles responses from the R307 sensor. The function waits for and processes the data received from the sensor via UART, ensuring communication is successful.

4. **`r307_response_parser()`**  
   Parses the responses received from the R307. This function extracts meaningful information (e.g., success/failure status, system parameters) from the sensor's response packet.

### Example Usage
Below is a brief example of how to initialize the R307 with the FTDI232 module:

### Communication Protocol
The R307 operates using a packet-based communication protocol over UART. Each packet consists of:
- **Packet Identifier**: A header identifying the start of a communication packet.
- **Packet Length**: Length of the following packet data.
- **Instruction Code**: Specifies the action to be performed (e.g., enroll, capture).
- **Checksum**: Used for packet integrity validation.

For detailed protocol information, refer to the [R307 User Manual](https://www.openhacks.com/uploadsproductos/r307_fingerprint_module_user_manual.pdf).

## Available Functions
The library provides the following core functions (based on the R307 sensor's user manual):
- Enroll new fingerprints
- Verify existing fingerprints
- Delete fingerprint data
- Set new module address and password
- Read system parameters (e.g., status, memory)
- Capture, search, and store fingerprint templates

For the full list of functions and their descriptions, refer to the source code.

## Limitations
- **Notepad Functions**: The `WriteNotepad` and `ReadNotepad` functions are not implemented yet.
- **Example Programs**: No complete example programs are available as of now, though the library is fully commented and can be easily extended.

## Future Work
- Implementation of the missing **Notepad** functions.
- Additional example programs for common tasks such as enrolling and searching fingerprints.
- Refactoring for better compatibility with other USB-to-UART bridges.

## Conclusion
This project demonstrates how to interface the **R307 Fingerprint Sensor Module** with a host system using the **FTDI232** for UART communication. The library provides a solid foundation for future development and customization, and the modular structure allows for easy extension to support additional R307 functions.

If you find this library useful or have any suggestions, feel free to contribute or raise issues!

## References
- [R307 User Manual](https://www.openhacks.com/uploadsproductos/r307_fingerprint_module_user_manual.pdf)

---
