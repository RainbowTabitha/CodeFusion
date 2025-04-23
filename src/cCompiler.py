# ============================================
# CodeFusion
# Author: Tabitha Hanegan (naylahanegan@gmail.com)
# Date: 4/21/2025
# License: MIT
# ===========================================

import subprocess
import sys
import os
import re
import platform

def get_gcc_command():
    # Determine the base path
    if getattr(sys, 'frozen', False):
        # If the application is frozen, use the executable's directory
        base_path = sys._MEIPASS
    else:
        # Otherwise, use the script's directory
        base_path = os.getcwd()

    # Construct the path to the GCC executable
    gcc_path = os.path.join(base_path, "dependencies", "powerpc-gcc", "bin", "powerpc-eabi-gcc.exe")

    # Ensure the path is valid and return the command list
    if os.path.exists(gcc_path):
        return [gcc_path]
    else:
        print(f"Error: GCC executable not found at {gcc_path}")
        return None

def compile_to_asm(filename):
    # Ensure the file has a .c extension
    if not filename.endswith(".c"):
        print("Error: Please provide a valid C file with a .c extension.")
        return
    
    # Extract the base name (without extension) for output file
    base_name = os.path.splitext(filename)[0]
    
    cmd = get_gcc_command()
    if not platform.system() == "Windows":
        cmd = ["wine"] + cmd
        env = {**os.environ, "WINEDEBUG": "-all"}
    else:
        env = None

    cmd.extend(["-mcpu=powerpc", "-S", "-fno-asynchronous-unwind-tables", "-fno-ident", "-fno-common", "-O1", "-fno-optimize-sibling-calls", filename, "-o", f"{base_name}.s"])

    try:
        # Run the compilation command
        subprocess.run(cmd, check=True, env=env)
        print(f"Compiled {filename} to {base_name}.s successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during compilation: {e}")

def append_codewrite_to_asm(asm_filename, codewrite_lst_filename):
    try:
        # Read the contents of the .codewrite.lst file
        with open(codewrite_lst_filename, 'r') as codewrite_file:
            codewrite_content = codewrite_file.read()

        # Read the contents of the assembly (.s) file
        with open(asm_filename, 'r') as asm_file:
            asm_content = asm_file.read()

        # Combine the .codewrite.lst content at the top of the .s file content
        combined_content = codewrite_content + "\n" + asm_content

        # Write the combined content back to the .s file
        with open(asm_filename, 'w') as asm_file:
            asm_file.write(combined_content)

        print(f"Appended {codewrite_lst_filename} to the top of {asm_filename}.")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error while appending {codewrite_lst_filename} to {asm_filename}: {e}")

def remove_gnu_attribute(asm_filename):
    try:
        with open(asm_filename, 'r') as asm_file:
            lines = asm_file.readlines()

        # Remove any line containing `.gnu_attribute`
        filtered_lines = [line for line in lines if '.gnu_attribute' not in line]

        # Write the filtered content back to the assembly file
        with open(asm_filename, 'w') as asm_file:
            asm_file.writelines(filtered_lines)

        print(f"Removed '.gnu_attribute' from {asm_filename}.")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error while removing '.gnu_attribute' from {asm_filename}: {e}")

def replace_bl_calls(asm_filename):
    try:
        with open(asm_filename, 'r') as asm_file:
            content = asm_file.read()

        # Replace instances of `bl func` with the new assembly structure
        def replacement(match):
            func_name = match.group(1)
            return (f"mr r0, r13\n"
                    f"	lis r13, {func_name}@ha\n"
                    f"	addi r13, r13, {func_name}@l\n"
                    f"	mtctr r13\n"
                    f"	mr r13, r0\n"
                    f"	bctrl\n")

        # Updated regex to match `bl` followed by exactly one space and then the function name
        new_content = re.sub(r'\bbl (\w+)', replacement, content)

        # Write the modified content back to the assembly file
        with open(asm_filename, 'w') as asm_file:
            asm_file.write(new_content)

        print(f"Replaced 'bl' calls in {asm_filename}.")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error while replacing 'bl' calls in {asm_filename}: {e}")

def update_include_paths(file_path, game_id):
    print("Updating include paths...")
    print(f"File path: {file_path}")
    print(f"Game ID: {game_id}")

    try:
        with open(file_path, 'r') as file:
            content = file.read()
        print("File content read successfully.")

        # Remove existing include for types.h
        content = re.sub(r'#include "include/types.h"', '', content)
        print("Removed existing include for types.h.")

        # Prepare new include paths
        new_includes = '#include "include/generic_types.h"\n'

        # Determine the base paths for includes
        if getattr(sys, 'frozen', False):
            base_include_paths = [sys._MEIPASS, os.getcwd()]
        else:
            base_include_paths = [os.getcwd()]

        # Recursively scan include/gc/ for .h files in both paths
        for base_include_path in base_include_paths:
            gc_include_dir = os.path.join(base_include_path, 'include', 'gc')
            for root, _, files in os.walk(gc_include_dir):
                for file in files:
                    if file.endswith('.h'):
                        relative_path = os.path.relpath(os.path.join(root, file), start='include')
                        new_includes += f'#include "../{relative_path}"\n'

            # Check for a header file matching the game_id in the include directory
            game_id_header = os.path.join(base_include_path, 'include', f'{game_id}.h')
            print(f"Looking for header file at: {game_id_header}")

            if os.path.exists(game_id_header):
                print(f"Header file found: {game_id_header}")
                new_includes += f'#include "include/{game_id}.h"\n'
            else:
                print(f"Header file not found: {game_id_header}")

        # Prepend new includes to the existing content
        updated_content = new_includes + content
        print("Prepended new includes to the content.")

        with open(file_path, 'w') as file:
            file.write(updated_content)
        print(f"Updated include paths in {file_path}.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error while updating include paths in {file_path}: {e}")
        print(f"Error while updating include paths in {file_path}: {e}")