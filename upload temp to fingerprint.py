import serial
import time

def calculate_checksum(packet):
    return sum(packet[6:]) & 0xFFFF

def send_command(command_packet):
    ser.write(command_packet)
    time.sleep(0.5)  # Adjust timing if necessary
    response = ser.read(ser.in_waiting or 12)  # Read response
    return response

ser = serial.Serial('COM3', baudrate=57600, timeout=1)

# Step: Upload the fingerprint template from the PC to CharBuffer1 in the module
buffer_id = 0x01  # Upload to CharBuffer1 (0x01 for CharBuffer1, 0x02 for CharBuffer2)

header = [0xEF, 0x01]          # Header for all packets
address = [0xFF, 0xFF, 0xFF, 0xFF]  # Default address
package_identifier = [0x01]    # Command package identifier
length = [0x00, 0x04]          # Length of the data section (4 bytes: instruction + buffer ID + checksum)
instruction_code = [0x08]      # Instruction code for UpChar

# Load the template data from the binary file
with open("fingerprint_template.bin", "rb") as file:
    template_data = file.read()

# Prepare the upload command packet
packet_without_checksum = header + address + package_identifier + length + instruction_code + [buffer_id]
checksum = calculate_checksum(packet_without_checksum)  # Calculate checksum for the command
checksum_bytes = [checksum >> 8, checksum & 0xFF]
command_packet = bytearray(packet_without_checksum + checksum_bytes)

# Send the initial upload command
ser.write(command_packet)
time.sleep(0.5)

# Send the template data in chunks (adjust according to your module's buffer size)
chunk_size = 128  # You can choose an appropriate size (e.g., 32, 64, 128 bytes)
for i in range(0, len(template_data), chunk_size):
    chunk = template_data[i:i + chunk_size]
    ser.write(chunk)
    time.sleep(0.05)  # Short delay between sending chunks

# Final response from the module after the data transfer
response = ser.read(ser.in_waiting)
if len(response) >= 12:
    confirmation_code = response[9]
    if confirmation_code == 0x00:
        print(f"Fingerprint template successfully uploaded to CharBuffer{buffer_id}.")
    else:
        print(f"Error: Received confirmation code {confirmation_code:02X}.")
else:
    print("No response or incomplete response received.")

ser.close()
