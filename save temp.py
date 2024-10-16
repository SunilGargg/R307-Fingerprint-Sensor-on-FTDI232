import serial
import time

def calculate_checksum(packet):
    return sum(packet[6:]) & 0xFFFF

def send_command(command_packet):
    ser.write(command_packet)
    time.sleep(1)  # Adjust timing if necessary
    response = ser.read(ser.in_waiting or 12)  # Read response
    return response

# Serial port configuration
ser = serial.Serial('COM3', baudrate=57600, timeout=2)  # Increase timeout

# Function to upload fingerprint data from specified CharBuffer
def upload_fingerprint(buffer_id):
    header = [0xEF, 0x01]
    address = [0xFF, 0xFF, 0xFF, 0xFF]
    package_identifier = [0x01]
    length = [0x00, 0x04]
    instruction_code = [0x08]
    packet_without_checksum = header + address + package_identifier + length + instruction_code + [buffer_id]
    checksum = calculate_checksum(packet_without_checksum)
    checksum_bytes = [checksum >> 8, checksum & 0xFF]
    command_packet = bytearray(packet_without_checksum + checksum_bytes)
    
    # Send upload command and get response
    ser.write(command_packet)
    time.sleep(1)
    
    response = ser.read(ser.in_waiting or 1024)  # Increase buffer size if necessary
    
    if len(response) > 12:
        print("Fingerprint template data received from CharBuffer{}:".format(buffer_id))
        print(response)  # Print response for debugging
        with open("fingerprint_template_{}.bin".format(buffer_id), "wb") as file:
            file.write(response)
        print("Fingerprint template saved to fingerprint_template_{}.bin.".format(buffer_id))
    else:
        print("Failed to upload the fingerprint template from CharBuffer{} or incomplete response received.".format(buffer_id))

# Upload from CharBuffer1
upload_fingerprint(0x01)  # For CharBuffer1

# Upload from CharBuffer2
upload_fingerprint(0x02)  # For CharBuffer2

# Close the serial connection
ser.close()
