# ============================================
# CodeFusion
# Author: Tabitha Hanegan (naylahanegan@gmail.com)
# Date: 4/21/2025
# License: MIT
# ===========================================

import re
import tempfile

def dtkSymbolsTxtToLst(input_file, output_file):
    pattern = re.compile(r'(\S+)\s*=\s*(?:\S+:)?(0x[0-9A-Fa-f]+);')

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            match = pattern.match(line)
            if match:
                label, address = match.groups()
                outfile.write(f'{address[2:]}:{label}\n')


def parse_lst_file(lst_file_path, output_filename):
    codewrite_lst = []

    if output_filename is None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.codewrite.lst') as temp_output_file:
            output_filename = temp_output_file.name

    try:
        with open(lst_file_path, 'r') as lst_file:
            for line in lst_file:
                # Split the line into address and symbol name
                line = line.strip()
                if not line or ':' not in line:
                    continue
                address, symbol = line.split(':')
                
                # Skip symbols that start with '@'
                if symbol.startswith('@'):
                    continue

                # Format the symbol in `.set` format
                formatted_line = f".set {symbol},0x{address.upper()}"
                codewrite_lst.append(formatted_line)
        
        # Write the formatted output to a .codewrite.lst file
        with open(output_filename, 'w') as output_file:
            output_file.write('\n'.join(codewrite_lst) + '\n')
        
        print(f"Parsed {lst_file_path} and wrote to {output_filename} successfully.")
    
    except FileNotFoundError:
        print(f"Error: File {lst_file_path} not found.")
    except Exception as e:
        print(f"Error while parsing {lst_file_path}: {e}")

    return output_filename 