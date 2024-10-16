import serial
import time

def calculate_checksum(packet):
    return sum(packet[6:]) & 0xFFFF

def send_command(command_packet):
    ser.write(command_packet)
    time.sleep(1)  # Adjust timing if necessary
    response = ser.read(ser.in_waiting or 12)  # Read response
    return response

def upload_fingerprint_template(buffer_id, file_path):
    # Step 1: Read the template data from the file
    with open(file_path, "rb") as file:
        template_data = file.read()
    
    # Step 2: Calculate the number of packets required
    packet_size = 64  # Adjust as necessary
    num_packets = (len(template_data) + packet_size - 1) // packet_size
    
    # Uploading the fingerprint template to the sensor
    for packet_number in range(num_packets):
        start_index = packet_number * packet_size
        end_index = start_index + packet_size
        packet_data = template_data[start_index:end_index]
        
        # Construct the packet
        header = [0xEF, 0x01]
        address = [0xFF, 0xFF, 0xFF, 0xFF]
        package_identifier = [0x02]  # Command for uploading data
        length = [0x00, 0x00]  # Will be updated with packet length
        instruction_code = [0x09]  # Instruction code for uploading fingerprint template
        packet_body = list(packet_data)
        checksum = calculate_checksum(header + address + package_identifier + length + instruction_code + packet_body)
        checksum_bytes = [checksum >> 8, checksum & 0xFF]
        
        # Update length field
        length = [len(packet_body) + 2]  # Data length + checksum
        command_packet = bytearray(header + address + package_identifier + length + instruction_code + packet_body + checksum_bytes)
        
        # Send packet
        response = send_command(command_packet)
        print(f"Response for packet {packet_number + 1}: {response}")
    
    # Confirm the upload
    confirmation_packet = header + address + package_identifier + [0x00, 0x04] + [0x0A] + [buffer_id]  # Instruction code 0x0A for confirming the upload
    checksum = calculate_checksum(confirmation_packet)
    checksum_bytes = [checksum >> 8, checksum & 0xFF]
    confirmation_packet += checksum_bytes
    response = send_command(bytearray(confirmation_packet))
    
    if b'\x00' in response:  # Check for success response
        print("Fingerprint template uploaded successfully.")
    else:
        print("Failed to upload fingerprint template.")

# Serial port configuration
ser = serial.Serial('COM3', baudrate=57600, timeout=2)

# Upload the fingerprint template1
upload_fingerprint_template(buffer_id=0x01, file_path="fingerprint_template_1.bin")

# Upload the fingerprint template2
#upload_fingerprint_template(buffer_id=0x02, file_path="fingerprint_template_2.bin")

# Close the serial connection
ser.close()
