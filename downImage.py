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

# Step 1: Send the command to prepare the sensor for image download

# Command packet to prepare for downloading the image
header = [0xEF, 0x01]          # Header for all packets
address = [0xFF, 0xFF, 0xFF, 0xFF]  # Default address
package_identifier = [0x01]    # Command package identifier
length = [0x00, 0x03]          # Length of the data section (3 bytes: instruction + checksum)
instruction_code = [0x0B]      # Instruction code for DownImage
packet_without_checksum = header + address + package_identifier + length + instruction_code
checksum = calculate_checksum(packet_without_checksum)
checksum_bytes = [checksum >> 8, checksum & 0xFF]
command_packet = bytearray(packet_without_checksum + checksum_bytes)  # Convert to bytearray

# Send the download image command and get response
response = send_command(command_packet)

# Step 2: Check for a valid response and start sending the image data

if response[9] == 0x00:
    print("Ready to receive the image data...")

    # Load the image data from a file
    with open("fingerprint_image.bmp", "rb") as file:
        image_data = file.read()

    # Break the image data into chunks of 64, 128, or 256 bytes as required by the protocol
    chunk_size = 128  # You can choose 64, 128, or 256 bytes per packet
    for i in range(0, len(image_data), chunk_size):
        packet_data = list(image_data[i:i + chunk_size])
        package_identifier = [0x02]  # Data packet identifier (0x02)
        length = [0x00, len(packet_data) + 2]  # Length of data section (data + 2 bytes for checksum)
        packet_without_checksum = header + address + package_identifier + length + packet_data
        checksum = calculate_checksum(packet_without_checksum)
        checksum_bytes = [checksum >> 8, checksum & 0xFF]
        data_packet = bytearray(packet_without_checksum + checksum_bytes)  # Convert to bytearray

        # Send the data packet to the sensor
        ser.write(data_packet)
        time.sleep(0.5)

        # Optionally, read acknowledgment after each chunk if needed
        ack_response = ser.read(ser.in_waiting or 12)
        if len(ack_response) < 12 or ack_response[9] != 0x00:
            print("Error in transferring data at chunk", i // chunk_size)
            break

    print("Image data successfully downloaded to the sensor.")
else:
    print("Failed to initiate image download or received an error.")

# Close the serial connection
ser.close()
