import serial
import time

# Function to calculate checksum
def calculate_checksum(packet):
    return sum(packet[6:]) & 0xFFFF

# Function to send command to R307 and receive the response
def send_command(command_packet):
    ser.write(command_packet)
    time.sleep(0.5)  # Adjust timing if necessary
    response = ser.read(ser.in_waiting or 12)  # Read response
    return response

# Serial port configuration (adjust COM port and baud rate as necessary)
ser = serial.Serial('COM3', baudrate=57600, timeout=1)

# Step: Upload the fingerprint template from CharBuffer1 to PC
buffer_id = 0x01  # Upload from CharBuffer1 (0x01 for CharBuffer1, 0x02 for CharBuffer2)

header = [0xEF, 0x01]          # Header for all packets
address = [0xFF, 0xFF, 0xFF, 0xFF]  # Default address
package_identifier = [0x01]    # Command package identifier
length = [0x00, 0x04]          # Length of the data section (4 bytes: instruction + buffer ID + checksum)
instruction_code = [0x08]      # Instruction code for UpChar
packet_without_checksum = header + address + package_identifier + length + instruction_code + [buffer_id]
checksum = calculate_checksum(packet_without_checksum)  # Calculate checksum
checksum_bytes = [checksum >> 8, checksum & 0xFF]  # Split checksum into two bytes
command_packet = bytearray(packet_without_checksum + checksum_bytes)  # Convert to bytearray

# Send upload command and get response
ser.write(command_packet)
time.sleep(0.5)

# Read the data response
response = ser.read(ser.in_waiting)  # Read all available data

# Check for a valid response
if len(response) > 12:
    print("Fingerprint template data received from CharBuffer1:")
    print(response)  # The template data is in the response
    # Save the template to a file
    with open("fingerprint_template.bin", "wb") as file:
        file.write(response)
    print("Fingerprint template saved to fingerprint_template.bin.")
else:
    print("Failed to upload the fingerprint template or incomplete response received.")

# Close the serial connection
ser.close()
