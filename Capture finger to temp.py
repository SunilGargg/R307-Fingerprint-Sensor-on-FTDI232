import serial
import time

def calculate_checksum(packet):
    return sum(packet[6:]) & 0xFFFF

def send_command(command_packet):
    ser.write(command_packet)
    time.sleep(1)  # Increase delay to ensure module has time to respond
    response = ser.read(ser.in_waiting or 12)  # Adjusted to read 12 bytes minimum
    return response


ser = serial.Serial('COM3', baudrate=57600, timeout=1)

### Step 1: Capture First Fingerprint Image
print("Step 1: Capture First Fingerprint Image")
header = [0xEF, 0x01]  # Header for all packets
address = [0xFF, 0xFF, 0xFF, 0xFF]  # Default address
package_identifier = [0x01]  # Command package identifier
length = [0x00, 0x03]  # Length of the data section (3 bytes: instruction + checksum)
instruction_code = [0x01]  # Instruction code for GenImg
packet_without_checksum = header + address + package_identifier + length + instruction_code
checksum = calculate_checksum(packet_without_checksum)  # Calculate checksum
checksum_bytes = [checksum >> 8, checksum & 0xFF]  # Split checksum into two bytes
command_packet = bytearray(packet_without_checksum + checksum_bytes)  # Convert to bytearray

response = send_command(command_packet)

# Parse the response
if len(response) >= 12:
    confirmation_code = response[9]
    if confirmation_code == 0x00:
        print("Fingerprint image captured successfully.")
    elif confirmation_code == 0x02:
        print("No finger detected. Please try again.")
        ser.close()
        exit()
    elif confirmation_code == 0x03:
        print("Failed to capture fingerprint image.")
        ser.close()
        exit()
    else:
        print(f"Error: Received confirmation code {confirmation_code:02X}.")
        ser.close()
        exit()
else:
    print("No response or incomplete response received.")
    ser.close()
    exit()

### Step 2: Convert the First Image to a Character File (CharBuffer1)
print("Step 2: Convert First Fingerprint Image to Character File (CharBuffer1)")
buffer_id = 0x01  # Store in CharBuffer1
length = [0x00, 0x04]  # Length of the data section (4 bytes: instruction + buffer ID + checksum)
instruction_code = [0x02]  # Instruction code for Img2Tz
packet_without_checksum = header + address + package_identifier + length + instruction_code + [buffer_id]
checksum = calculate_checksum(packet_without_checksum)  # Calculate checksum
checksum_bytes = [checksum >> 8, checksum & 0xFF]  # Split checksum into two bytes
command_packet = bytearray(packet_without_checksum + checksum_bytes)  # Convert to bytearray

response = send_command(command_packet)

# Parse the response
if len(response) >= 12:
    confirmation_code = response[9]
    if confirmation_code == 0x00:
        print("First fingerprint image successfully converted to character file in CharBuffer1.")
    elif confirmation_code == 0x06:
        print("Failed to generate character file due to the poor quality of the fingerprint image.")
        ser.close()
        exit()
    elif confirmation_code == 0x07:
        print("Failed to generate character file due to the lack of character points or image being too small.")
        ser.close()
        exit()
    else:
        print(f"Error: Received confirmation code {confirmation_code:02X}.")
        ser.close()
        exit()
else:
    print("No response or incomplete response received.")
    ser.close()
    exit()

### Step 3: Capture Second Fingerprint Image
print("Step 3: Capture Second Fingerprint Image")
header = [0xEF, 0x01]  # Header for all packets
address = [0xFF, 0xFF, 0xFF, 0xFF]  # Default address
package_identifier = [0x01]  # Command package identifier
length = [0x00, 0x03]  # Length of the data section (3 bytes: instruction + checksum)
instruction_code = [0x01]  # Instruction code for GenImg
packet_without_checksum = header + address + package_identifier + length + instruction_code
checksum = calculate_checksum(packet_without_checksum)  # Calculate checksum
checksum_bytes = [checksum >> 8, checksum & 0xFF]  # Split checksum into two bytes
command_packet = bytearray(packet_without_checksum + checksum_bytes)  # Convert to bytearray

response = send_command(command_packet)

if len(response) >= 12 and response[9] == 0x00:
    print("Second fingerprint image captured successfully.")
else:
    print("Failed to capture the second fingerprint image.")
    ser.close()
    exit()

### Step 4: Convert the Second Image to a Character File (CharBuffer2)
buffer_id = 0x02  # Store in CharBuffer2 (0x01 for CharBuffer1, 0x02 for CharBuffer2)
length = [0x00, 0x04]          # Length of the data section (4 bytes: instruction + buffer ID + checksum)
instruction_code = [0x02]      # Instruction code for Img2Tz
packet_without_checksum = header + address + package_identifier + length + instruction_code + [buffer_id]
checksum = calculate_checksum(packet_without_checksum)
checksum_bytes = [checksum >> 8, checksum & 0xFF]
command_packet = bytearray(packet_without_checksum + checksum_bytes)

response = send_command(command_packet)
if len(response) >= 12 and response[9] == 0x00:
    print("Second fingerprint image successfully converted to character file in CharBuffer2.")
else:
    print("Failed to convert the second fingerprint image.")
    ser.close()
    exit()

### Step 5: Combine the Two Character Files into a Template
print("Step 5: Combine Character Files into a Template")
instruction_code = [0x05]  # Instruction code for RegModel
packet_without_checksum = header + address + package_identifier + [0x00, 0x03] + instruction_code
checksum = calculate_checksum(packet_without_checksum)  # Calculate checksum
checksum_bytes = [checksum >> 8, checksum & 0xFF]  # Split checksum into two bytes
command_packet = bytearray(packet_without_checksum + checksum_bytes)  # Convert to bytearray

response = send_command(command_packet)

# Parse the response
if len(response) >= 12:
    confirmation_code = response[9]
    if confirmation_code == 0x00:
        print("Character files successfully combined into a fingerprint template.")
    elif confirmation_code == 0x0A:
        print("Failed to combine character files; they do not match.")
        ser.close()
        exit()
    else:
        print(f"Error: Received confirmation code {confirmation_code:02X}.")
        ser.close()
        exit()
else:
    print("No response or incomplete response received.")
    ser.close()
    exit()

### Step 6: Store the Fingerprint Template in the Library
print("Step 6: Store the Fingerprint Template in the Library")
buffer_id = 0x01  # Store from CharBuffer1
page_id = 0x0001  # The location where the template will be stored (PageID, 2 bytes)
header = [0xEF, 0x01]          # Header for all packets
address = [0xFF, 0xFF, 0xFF, 0xFF]  # Default address
package_identifier = [0x01]    # Command package identifier
length = [0x00, 0x06]          # Length of the data section (6 bytes: instruction + buffer ID + PageID + checksum)
instruction_code = [0x06]  # Instruction code for Store
page_id_bytes = [page_id >> 8, page_id & 0xFF]  # Convert PageID to two bytes (high byte first)
packet_without_checksum = header + address + package_identifier + [0x00, 0x06] + instruction_code + [buffer_id] + page_id_bytes
checksum = calculate_checksum(packet_without_checksum)  # Calculate checksum
checksum_bytes = [checksum >> 8, checksum & 0xFF]  # Split checksum into two bytes
command_packet = bytearray(packet_without_checksum + checksum_bytes)  # Convert to bytearray

response = send_command(command_packet)

# Parse the response
if len(response) >= 12:
    confirmation_code = response[9]
    if confirmation_code == 0x00:
        print(f"Fingerprint template successfully stored at PageID {page_id}.")
        
        # Save the PageID to a notepad file
        with open("fingerprint_templates.txt", "a") as file:
            file.write(f"Fingerprint template stored at PageID: {page_id}\n")
        print(f"PageID {page_id} saved to fingerprint_templates.txt.")

    elif confirmation_code == 0x0B:
        print("Error: The PageID is beyond the library's capacity.")
    elif confirmation_code == 0x18:
        print("Error: Failed to write the template to the library.")
    else:
        print(f"Error: Received confirmation code {confirmation_code:02X}.")
else:
    print("No response or incomplete response received.")

ser.close()
