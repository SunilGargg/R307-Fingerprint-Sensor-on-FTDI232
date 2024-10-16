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

# Step 6: Search the fingerprint library for a match
buffer_id = 0x01  # Search using CharBuffer1
start_page = 0x0000  # Start searching from the beginning of the library
page_num = 0x03E8  # Number of pages to search (1000 pages)

# Step 6.1: Capture the fingerprint image
header = [0xEF, 0x01]          # Header for all packets
address = [0xFF, 0xFF, 0xFF, 0xFF]  # Default address
package_identifier = [0x01]    # Command package identifier
length = [0x00, 0x03]          # Length of the data section (3 bytes: instruction + checksum)
instruction_code = [0x01]      # Instruction code for GenImg
packet_without_checksum = header + address + package_identifier + length + instruction_code
checksum = calculate_checksum(packet_without_checksum)
checksum_bytes = [checksum >> 8, checksum & 0xFF]
command_packet = bytearray(packet_without_checksum + checksum_bytes)

# Send capture command and get response
response = send_command(command_packet)
if len(response) >= 12 and response[9] == 0x00:
    print("Fingerprint image captured successfully.")
else:
    print("Failed to capture the fingerprint image.")
    ser.close()
    exit()

# Step 6.2: Convert the captured image to a character file in CharBuffer1
instruction_code = [0x02]  # Instruction code for Img2Tz
length = [0x00, 0x04]  # Length of the data section (4 bytes: instruction + buffer ID + checksum)
packet_without_checksum = header + address + package_identifier + length + instruction_code + [buffer_id]
checksum = calculate_checksum(packet_without_checksum)
checksum_bytes = [checksum >> 8, checksum & 0xFF]
command_packet = bytearray(packet_without_checksum + checksum_bytes)

# Send convert command and get response
response = send_command(command_packet)
if len(response) >= 12 and response[9] == 0x00:
    print("Fingerprint image successfully converted to character file in CharBuffer1.")
else:
    print("Failed to convert the fingerprint image.")
    ser.close()
    exit()

# Step 6.3: Search the fingerprint library for a match
instruction_code = [0x04]  # Instruction code for Search
start_page_bytes = [start_page >> 8, start_page & 0xFF]  # Convert StartPage to two bytes
page_num_bytes = [page_num >> 8, page_num & 0xFF]  # Convert PageNum to two bytes
packet_without_checksum = header + address + package_identifier + [0x00, 0x08] + instruction_code + [buffer_id] + start_page_bytes + page_num_bytes
checksum = calculate_checksum(packet_without_checksum)
checksum_bytes = [checksum >> 8, checksum & 0xFF]
command_packet = bytearray(packet_without_checksum + checksum_bytes)

# Send search command and get response
response = send_command(command_packet)

# Parse the response
if len(response) >= 16:  # The response will be longer than 12 bytes if a match is found
    confirmation_code = response[9]
    if confirmation_code == 0x00:
        page_id = (response[10] << 8) | response[11]  # Combine two bytes to form PageID
        match_score = (response[12] << 8) | response[13]  # Combine two bytes to form MatchScore
        print(f"Match found! PageID: {page_id}, Match Score: {match_score}")
    elif confirmation_code == 0x09:
        print("No matching fingerprint found in the library.")
    else:
        print(f"Error: Received confirmation code {confirmation_code:02X}.")
else:
    print("No response or incomplete response received.")

# Close the serial connection
ser.close()
