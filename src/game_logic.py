# ============================================
# CodeFusion
# Author: Tabitha Hanegan (naylahanegan@gmail.com)
# Date: 4/21/2025
# License: MIT
# ===========================================

import os
import subprocess
import platform
from CTkMessagebox import CTkMessagebox
import gecko
import utils
import sys
import os
from cCompiler import compile_to_asm, append_codewrite_to_asm, remove_gnu_attribute, replace_bl_calls, update_include_paths
from symbol_processor import dtkSymbolsTxtToLst, parse_lst_file
import re

class GameLogic:
    def handle_geckoos_code(self, app):
        if app.selected_game != None:
            self.add_symbols_to_temp_asm(app)
        else:
            input_text = app.inputCode.get("1.0", "end-1c")
            with open("temp.asm", "w") as temp_file:
                temp_file.write(input_text)

        input_text = app.inputCode.get("1.0", "end-1c")
        app.output.delete("1.0", "end")
        app.output.insert("1.0", input_text)

    def add_symbols_to_temp_asm(self, app):
        game_id = utils.GAME_TO_ID[app.selected_game]
        symbol_file_path = os.path.join(os.getcwd(), f"symbols/{game_id}.sym")

        dtkSymbolsTxtToLst(symbol_file_path, "temp.out")
        output_filename = parse_lst_file("temp.out", "temp_codewrite.out")

        with open(output_filename, 'r') as output_file:
            generated_code = output_file.read()

        input_text = app.inputCode.get("1.0", "end-1c")
        compiled_code = generated_code + "\n" + input_text

        if not os.path.exists('temp.asm'):
            open('temp.asm', 'w').close()
            
        with open('temp.asm', 'r+') as temp_file:
            existing_content = temp_file.read()
            temp_file.seek(0)
            temp_file.write(compiled_code + "\n" + existing_content)

        print("Successfully added symbols to the temp.asm file.")

    def get_gcc_gekko_command(self):
        # Determine the base path
        if getattr(sys, 'frozen', False):
            # If the application is frozen, use the executable's directory
            base_path = sys._MEIPASS
        else:
            # Otherwise, use the script's directory
            base_path = os.getcwd()

        # Construct the path to the GCC executable
        gcc_path = os.path.join(base_path, "dependencies", "codewrite", "powerpc-gekko-as.exe")
        print(gcc_path)
        cmd = [gcc_path]
        return cmd

    def handle_powerpc_asm(self, app):
        if app.selected_game != None:
            self.add_symbols_to_temp_asm(app)
        else:
            input_text = app.inputCode.get("1.0", "end-1c")
            with open("temp.asm", "w") as temp_file:
                temp_file.write(input_text)

        cmd = self.get_gcc_gekko_command()
        if not platform.system() == "Windows":
            cmd = ["wine"] + cmd
            env = {**os.environ, "WINEDEBUG": "-all"}
        else:
            env = None

        cmd.extend(["-a32", "-mbig", "-mregnames", "-mgekko", "temp.asm"])

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            start_address = app.insertionAddress.get("1.0", "end-1c")
            gecko.convert_aout_to_gecko('a.out', start_address, 'b.out', overwrite=False)
            with open("b.out", "r") as output_file:
                output_text = output_file.read()
            app.output.delete("1.0", "end")
            app.output.insert("1.0", output_text)

            CTkMessagebox(message="Patched successfully.", title="Success", icon="check", option_1="OK")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode()
            CTkMessagebox(message=f"Error occurred: {error_msg}", title="Error", icon="warning", option_1="OK")
        finally:
            for file in ["temp.asm", "a.out", "b.out", "temp.out", "temp_codewrite.out"]:
                try:
                    os.remove(file)
                except:
                    for file in ["temp.asm", "a.out", "b.out", "temp.out", "temp_codewrite.out"]:
                        try:
                            os.remove(file)
                        except:
                            pass

    def handle_c_code(self, app):
        input_text = app.inputCode.get("1.0", "end-1c")
        with open("temp.c", "w") as temp_file:
            temp_file.write(input_text)
        if app.selected_game != None:
            game_id = utils.GAME_TO_ID[app.selected_game]
        else:
            game_id = "generic"
        update_include_paths("temp.c", game_id)
        try:
            if not compile_to_asm("temp.c"):
                return
        except Exception as e:
            print(f"An error occurred: {e}")
            return

        if app.selected_game != None:
            symbol_file_path = os.path.join(os.getcwd(), f"symbols/{game_id}.sym")
            dtkSymbolsTxtToLst(symbol_file_path, "temp.out")
            output_filename = parse_lst_file("temp.out", "temp_codewrite.out")
            asm_filename = "temp.s"
            append_codewrite_to_asm(asm_filename, "temp_codewrite.out")

        # Remove .gnu_attribute from the generated .s file
        asm_filename = "temp.s"
        remove_gnu_attribute(asm_filename)

        # Replace `bl` calls in the generated .s file
        replace_bl_calls(asm_filename)
        
        cmd = self.get_gcc_gekko_command()
        if not platform.system() == "Windows":
            cmd = ["wine"] + cmd
            env = {**os.environ, "WINEDEBUG": "-all"}
        else:
            env = None

        cmd.extend(["-a32", "-mbig", "-mregnames", "-mgekko", asm_filename])

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            start_address = app.insertionAddress.get("1.0", "end-1c")
            gecko.convert_aout_to_gecko('a.out', start_address, 'b.out', overwrite=False)
            with open("b.out", "r") as output_file:
                output_text = output_file.read()
            app.output.delete("1.0", "end")
            app.output.insert("1.0", output_text)

            CTkMessagebox(message="Patched successfully.", title="Success", icon="check", option_1="OK")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode()
            CTkMessagebox(message=f"Error occurred: {error_msg}", title="Error", icon="warning", option_1="OK")
        finally:
            for file in ["temp.asm", "a.out", "b.out", "temp.c", "temp.s", "temp.out", "temp_codewrite.out"]:
                try:
                    os.remove(file)
                except:
                    for file in ["temp.asm", "a.out", "b.out", "temp.c", "temp.s", "temp.out", "temp_codewrite.out"]:
                        try:
                            os.remove(file)
                        except:
                            pass