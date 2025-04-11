# ============================================
# CodeFusion
# Author: Tabitha Hanegan (naylahanegan@gmail.com)
# Date: 4/10/2025
# License: MIT
# ============================================

import re
import argparse

def dtkSymbolsTxtToLst(input_file, output_file):
    pattern = re.compile(r'(\S+)\s*=\s*(?:\S+:)?(0x[0-9A-Fa-f]+);')

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            match = pattern.match(line)
            if match:
                label, address = match.groups()
                outfile.write(f'{address[2:]}:{label}\n')

def main():
    parser = argparse.ArgumentParser(description='Parse input symbol file and write formatted output.')
    parser.add_argument('input_file', help='Path to the input file')
    parser.add_argument('output_file', help='Path to the output file')

    args = parser.parse_args()
    parse_input_file(args.input_file, args.output_file)

if __name__ == '__main__':
    main()