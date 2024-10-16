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

# Step: Delete the fingerprint template from the library
page_id = 0x0001  # The location (PageID) of the template to delete
num_of_templates = 0x0001  # Number of templates to delete starting from PageID

header = [0xEF, 0x01]          # Header for all packets
address = [0xFF, 0xFF, 0xFF, 0xFF]  # Default address
package_identifier = [0x01]    # Command package identifier
length = [0x00, 0x07]          # Length of the data section (7 bytes: instruction + PageID + Num + checksum)
instruction_code = [0x0C]      # Instruction code for DeletChar
page_id_bytes = [page_id >> 8, page_id & 0xFF]  # Convert PageID to two bytes (high byte first)
num_of_templates_bytes = [num_of_templates >> 8, num_of_templates & 0xFF]  # Convert Num to two bytes (high byte first)
packet_without_checksum = header + address + package_identifier + length + instruction_code + page_id_bytes + num_of_templates_bytes
checksum = calculate_checksum(packet_without_checksum)  # Calculate checksum
checksum_bytes = [checksum >> 8, checksum & 0xFF]  # Split checksum into two bytes
command_packet = bytearray(packet_without_checksum + checksum_bytes)  # Convert to bytearray

response = send_command(command_packet)

if len(response) >= 12:
    confirmation_code = response[9]
    if confirmation_code == 0x00:
        print(f"Fingerprint template at PageID {page_id} deleted successfully.")
    elif confirmation_code == 0x10:
        print("Error: Failed to delete the template.")
    else:
        print(f"Error: Received confirmation code {confirmation_code:02X}.")
else:
    print("No response or incomplete response received.")

ser.close()
