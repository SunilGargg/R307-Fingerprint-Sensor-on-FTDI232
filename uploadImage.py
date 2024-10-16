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

# Step 1: Send the command to upload the image from Img_Buffer to the computer

# Command packet to upload the image
header = [0xEF, 0x01]          # Header for all packets
address = [0xFF, 0xFF, 0xFF, 0xFF]  # Default address
package_identifier = [0x01]    # Command package identifier
length = [0x00, 0x03]          # Length of the data section (3 bytes: instruction + checksum)
instruction_code = [0x0A]      # Instruction code for UpImage
packet_without_checksum = header + address + package_identifier + length + instruction_code
checksum = calculate_checksum(packet_without_checksum)
checksum_bytes = [checksum >> 8, checksum & 0xFF]
command_packet = bytearray(packet_without_checksum + checksum_bytes)  # Convert to bytearray

# Send the upload image command and get response
response = send_command(command_packet)

# Step 2: Check for a valid response and start receiving the image data

if response[9] == 0x00:
    print("Ready to transfer the image data...")

    # Now receive the image data in chunks
    image_data = bytearray()
    while True:
        packet = ser.read(600)  # Read the next chunk of data (size can vary)
        
        if len(packet) == 0:
            break

        image_data.extend(packet)

        # Optionally, you can send an acknowledge after each chunk if needed
        # (based on protocol specifics, usually not necessary for continuous read)

    # Save the received image data to a file
    with open("fingerprint_image.bmp", "wb") as file:
        file.write(image_data)
    
    print("Fingerprint image data saved to fingerprint_image.bmp.")

else:
    print("Failed to upload the image or received an error.")

# Close the serial connection
ser.close()
