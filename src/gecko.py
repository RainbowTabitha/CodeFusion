# ============================================
# CodeFusion
# Author: Tabitha Hanegan (naylahanegan@gmail.com)
# Date: 4/21/2025
# License: MIT
# ===========================================

import struct

def remove_unnecessary_blank_lines(text):
    # Split the text into lines
    lines = text.splitlines()
    
    # Filter out all blank lines
    filtered_lines = [line for line in lines if line.strip()]

    # Join the lines back into a single string
    return "\n".join(filtered_lines) 

def convert_aout_to_gecko(input_file, start_address, output_file, overwrite=False):
    # Read the a.out file
    with open(input_file, 'rb') as f:
        data = f.read()
    
    # Extract relevant data
    data = data[52:data.index(b'\x00\x2E\x73\x79\x6D\x74\x61\x62')]  # Adjusted for Python
    
    # Prepare the output code
    code = []
    
    # Ensure start_address is a string before conversion
    if not start_address:  # Check if start_address is empty or None
        start_address = '0x80000000'  # Default value
    elif not start_address.startswith('0x'):  # Check if it doesn't start with '0x'
        start_address = '0x' + start_address  # Add '0x' prefix

    start_address_int = int(start_address, 16) & 0xFFFFFFFF  # Convert and format the starting address

    # Swap the first two bytes if necessary
    first_byte = (start_address_int >> 24) & 0xFF  # Get the first byte
    if start_address_int == 0x80000000:  # Check if start_address is 0x80000000
        start_address_int = (start_address_int & ~0xFF000000) | (0xC0 << 24)  # Set to C0
    elif first_byte == 0x80:
        if overwrite:
            start_address_int = (start_address_int & ~0xFF000000) | (0x06 << 24)  # Swap 80 to C2
        else:
            start_address_int = (start_address_int & ~0xFF000000) | (0xC2 << 24)  # Swap 80 to C2
    elif first_byte == 0x81:
        if overwrite:
            start_address_int = (start_address_int & ~0xFF000000) | (0x16 << 24)  # Swap 80 to C2
        else:
            start_address_int = (start_address_int & ~0xFF000000) | (0xD2 << 24)  # Swap 81 to D2    
    
    # Prepare the output code with spacing
    counter = 0
    for b in data:
        if counter % 8 == 0 and counter != 0:
            code.append("\n")  # New line after every 8 bytes
    
        if counter % 4 == 0 and counter % 8 != 0 and counter != 0:
            code.append(" ")  # Add space after every 4 bytes
    
        code.append(f"{b:02X}")  # Append the byte in hex format
        counter += 1
    
    # Add padding if necessary
    if not overwrite:
        if counter % 8 != 0:
            code.append(" 00000000")  # Add padding if not a multiple of 8
    
    if overwrite:
        num_lines = (len(data))  # Calculate number of lines (rounding up) and add 1 for the final line
    else:
        num_lines = (len(data) + 7) // 8  # Calculate number of lines (rounding up) and add 1 for the final line
    
    # Add the initial line with the starting address and number of lines
    code.insert(0, f"{start_address_int:08X} {num_lines:08X}\n")  # Insert at the beginning
    
    if not overwrite and len(data) % 8 == 0:
            code.append("\n60000000 00000000")  # Final line only if complete
    
    if overwrite:
        if not len(data) % 8 == 0:
            code.append(" 00000000")
    
    code.append(f"\n")
    
    # Join the code into a single string
    formatted_code = ''.join(code)
    
    if not overwrite and formatted_code.strip().endswith("60000000 00000000"):
        first_line = formatted_code.splitlines()[0]  # Get the first line
        address_part = first_line.split()[1]  # Get the second half (the number of lines)
        new_address = hex(int(address_part, 16) + 1)[2:].upper().zfill(8)  # Add 1 and format
        formatted_code = formatted_code.replace(address_part, new_address, 1)
    
    formatted_code = remove_unnecessary_blank_lines(formatted_code)


    
    # Write to dist/code.txt
    with open(output_file, "w") as output_file:
        output_file.write(remove_unnecessary_blank_lines(formatted_code))
