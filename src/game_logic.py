import os
import subprocess
import platform
import sys
from CTkMessagebox import CTkMessagebox
import gecko
import utils
from cCompiler import compile_to_asm, append_codewrite_to_asm, remove_gnu_attribute, replace_bl_calls, update_include_paths
from symbol_processor import dtkSymbolsTxtToLst, parse_lst_file

class GameLogic:
    def __init__(self):
        # Determine the base path once during initialization
        if getattr(sys, 'frozen', False):
            self.base_path = sys._MEIPASS
        else:
            self.base_path = os.getcwd()
        
    def _get_environment(self):
        """Return the appropriate environment based on platform"""
        if platform.system() != "Windows":
            return {**os.environ, "WINEDEBUG": "-all"}
        return None

    def _create_temp_asm(self, app):
        """Create a temporary assembly file with input code"""
        input_text = app.inputCode.get("1.0", "end-1c")
        with open("temp.asm", "w") as temp_file:
            temp_file.write(input_text)
            
    def _cleanup_files(self, files_to_clean=None):
        """Clean up temporary files"""
        if files_to_clean is None:
            files_to_clean = ["temp.asm", "a.out", "b.out", "b.txt", "temp.out", "temp_codewrite.out", "temp.c", "temp.s"]
        
        for file in files_to_clean:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except:
                pass

    def get_gcc_gekko_command(self):
        """Get the GCC Gekko command with appropriate path"""
        gcc_path = os.path.join(self.base_path, "dependencies", "codewrite", "powerpc-gekko-as.exe")
        print(gcc_path)
        cmd = [gcc_path]
        if platform.system() != "Windows":
            cmd = ["wine"] + cmd
        return cmd

    def add_symbols_to_temp_asm(self, app):
        """Add symbols to the temp assembly file"""
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

    def prepare_rom_path(self, rom_path):
        """Convert RVZ to ISO if needed"""
        if not rom_path.endswith(".rvz"):
            return rom_path
            
        env = self._get_environment()
        if platform.system() == "Windows":
            dolphin_tool_path = os.path.join(self.base_path, "dependencies", "dolphintool.exe")
        else:
            dolphin_tool_path = "dolphintool"
            
        cmd = [dolphin_tool_path, "convert", "-i", rom_path, "-f", "iso", "-o", "tmp.iso"]
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            return "tmp.iso"
        else:
            error_msg = result.stderr if result.stderr else "Unknown error occurred."
            raise RuntimeError(f"RVZ to ISO conversion failed: {error_msg}")

    def extract_iso(self, rom_path):
        """Extract ISO to tmp folder"""
        py_iso_tools_path = os.path.join(self.base_path, "dependencies", "pyisotools.exe")
        if not os.path.exists(py_iso_tools_path):
            raise FileNotFoundError(f"PyISOTools not found at: {py_iso_tools_path}")
            
        env = self._get_environment()
        cmd = [py_iso_tools_path]
        if platform.system() != "Windows":
            cmd = ["wine"] + cmd
            
        cmd += [rom_path, "E", "--dest=tmp/"]
        result = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            error_msg = result.stderr.decode() if result.stderr else "Unknown error occurred."
            raise RuntimeError(f"Game extraction failed: {error_msg}")

    def patch_dol_with_gecko(self, gecko_code_file):
        """Patch DOL file with Gecko codes"""
        gecko_loader_path = os.path.join(self.base_path, "dependencies", "GeckoLoader.exe")
        if not os.path.exists(gecko_loader_path):
            raise FileNotFoundError(f"GeckoLoader not found at: {gecko_loader_path}")
            
        env = self._get_environment()
        cmd = [gecko_loader_path]
        if platform.system() != "Windows":
            cmd = ["wine"] + cmd
            
        cmd += ["--hooktype=GX", "--optimize", "tmp/root/sys/main.dol", gecko_code_file, "--dest", "tmp/root/sys/main.dol"]
        result = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            error_msg = result.stderr.decode() if result.stderr else "Unknown error occurred."
            raise RuntimeError(f"Game patching failed: {error_msg}")

    def rebuild_iso(self, original_path):
        """Rebuild ISO from extracted files"""
        output_path = original_path[:-4] + "_modified.iso"
        py_iso_tools_path = os.path.join(self.base_path, "dependencies", "pyisotools.exe")
        if not os.path.exists(py_iso_tools_path):
            raise FileNotFoundError(f"PyISOTools not found at: {py_iso_tools_path}")
            
        env = self._get_environment()
        cmd = [py_iso_tools_path]
        if platform.system() != "Windows":
            cmd = ["wine"] + cmd
            
        cmd += ["tmp/root", "B", f"--dest={output_path}"]
        result = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            error_msg = result.stderr.decode() if result.stderr else "Unknown error occurred."
            raise RuntimeError(f"ISO rebuilding failed: {error_msg}")
            
        return output_path

    def convert_iso_to_rvz(self, iso_path, original_rvz_path):
        """Convert ISO back to RVZ if original was RVZ"""
        if platform.system() == "Windows":
            dolphin_tool_path = os.path.join(self.base_path, "dependencies", "dolphintool.exe")
        else:
            dolphin_tool_path = "dolphintool"
            
        env = self._get_environment()
        cmd = [dolphin_tool_path, "convert", "-i", iso_path, "-f", "rvz", "-o", original_rvz_path, 
               "-b", "131072", "-c", "zstd", "-l", "5"]
               
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else "Unknown error occurred."
            raise RuntimeError(f"ISO to RVZ conversion failed: {error_msg}")

    def process_rom(self, app, gecko_code_file):
        """Process ROM with Gecko codes"""
        rom_file_path = app.rom_file_entry.get()
        if not rom_file_path:
            CTkMessagebox(message="No ROM file selected.", title="Error", icon="warning", option_1="OK")
            return False
            
        try:
            # Process ROM
            working_rom_path = self.prepare_rom_path(rom_file_path)
            self.extract_iso(working_rom_path)
            self.patch_dol_with_gecko(gecko_code_file)
            modified_iso = self.rebuild_iso(rom_file_path)
            
            # Convert back to RVZ if needed
            if rom_file_path.endswith(".rvz"):
                self.convert_iso_to_rvz(modified_iso, rom_file_path[:-4] + "_modified.rvz")
                
            CTkMessagebox(message="Patched successfully.", title="Success", icon="check", option_1="OK")
            return True
            
        except Exception as e:
            CTkMessagebox(message=f"Error occurred: {str(e)}", title="Error", icon="warning", option_1="OK")
            return False

    def handle_geckoos_code(self, app):
        """Handle Gecko OS Code"""
        try:
            if app.selected_game is not None:
                self.add_symbols_to_temp_asm(app)
            else:
                self._create_temp_asm(app)

            input_text = app.inputCode.get("1.0", "end-1c")
            app.output.delete("1.0", "end")
            app.output.insert("1.0", input_text)
            
        except Exception as e:
            CTkMessagebox(message=f"Error occurred: {str(e)}", title="Error", icon="warning", option_1="OK")
        finally:
            self._cleanup_files()

    def handle_powerpc_asm(self, app):
        """Handle PowerPC Assembly Code"""
        try:
            if app.selected_game is not None:
                self.add_symbols_to_temp_asm(app)
            else:
                self._create_temp_asm(app)

            cmd = self.get_gcc_gekko_command()
            cmd.extend(["-a32", "-mbig", "-mregnames", "-mgekko", "temp.asm"])
            env = self._get_environment()

            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            start_address = app.insertionAddress.get("1.0", "end-1c")
            gecko.convert_aout_to_gecko('a.out', start_address, 'b.out', overwrite=False)
            
            with open("b.out", "r") as output_file:
                output_text = output_file.read()
            app.output.delete("1.0", "end")
            app.output.insert("1.0", output_text)

            CTkMessagebox(message="Patched successfully.", title="Success", icon="check", option_1="OK")
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            CTkMessagebox(message=f"Error occurred: {error_msg}", title="Error", icon="warning", option_1="OK")
        except Exception as e:
            CTkMessagebox(message=f"Error occurred: {str(e)}", title="Error", icon="warning", option_1="OK")
        finally:
            self._cleanup_files()

    def handle_c_code(self, app):
        """Handle C Code"""
        try:
            # Write C code to temp file
            input_text = app.inputCode.get("1.0", "end-1c")
            with open("temp.c", "w") as temp_file:
                temp_file.write(input_text)
                
            # Set game ID and update include paths
            game_id = utils.GAME_TO_ID.get(app.selected_game, "generic")
            update_include_paths("temp.c", game_id)
            
            # Compile C to ASM
            if not compile_to_asm("temp.c"):
                return
                
            # Process symbols if game is selected
            if app.selected_game is not None:
                symbol_file_path = os.path.join(os.getcwd(), f"symbols/{game_id}.sym")
                dtkSymbolsTxtToLst(symbol_file_path, "temp.out")
                output_filename = parse_lst_file("temp.out", "temp_codewrite.out")
                asm_filename = "temp.s"
                append_codewrite_to_asm(asm_filename, "temp_codewrite.out")

            # Clean up ASM file
            asm_filename = "temp.s"
            remove_gnu_attribute(asm_filename)
            replace_bl_calls(asm_filename)
            
            # Compile ASM with GCC
            cmd = self.get_gcc_gekko_command()
            cmd.extend(["-a32", "-mbig", "-mregnames", "-mgekko", asm_filename])
            env = self._get_environment()
            
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            
            # Convert to Gecko code
            start_address = app.insertionAddress.get("1.0", "end-1c")
            gecko.convert_aout_to_gecko('a.out', start_address, 'b.out', overwrite=False)
            
            # Display output
            with open("b.out", "r") as output_file:
                output_text = output_file.read()
            app.output.delete("1.0", "end")
            app.output.insert("1.0", output_text)

            CTkMessagebox(message="Patched successfully.", title="Success", icon="check", option_1="OK")
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            CTkMessagebox(message=f"Error occurred: {error_msg}", title="Error", icon="warning", option_1="OK")
        except Exception as e:
            CTkMessagebox(message=f"Error occurred: {str(e)}", title="Error", icon="warning", option_1="OK")
        finally:
            self._cleanup_files()

    def handle_powerpc_asm_rom(self, app):
        """Handle PowerPC Assembly Code for ROM patching"""
        try:
            # Create ASM file
            if app.selected_game is not None:
                self.add_symbols_to_temp_asm(app)
            else:
                self._create_temp_asm(app)

            # Compile ASM
            cmd = self.get_gcc_gekko_command()
            cmd.extend(["-a32", "-mbig", "-mregnames", "-mgekko", "temp.asm"])
            env = self._get_environment()
            
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            
            # Convert to Gecko code
            start_address = app.insertionAddress.get("1.0", "end-1c")
            gecko.convert_aout_to_gecko('a.out', start_address, 'b.out', overwrite=False)
            
            # Create Gecko code file
            with open("b.out", "r") as output_file:
                output_text = output_file.read()
                
            with open("b.txt", "w") as output_file:
                output_file.write("$CodeFusion\n" + output_text)
                
            # Process ROM
            self.process_rom(app, "b.txt")
            
        except Exception as e:
            CTkMessagebox(message=f"Error occurred: {str(e)}", title="Error", icon="warning", option_1="OK")
        finally:
            self._cleanup_files()

    def handle_c_code_rom(self, app):
        """Handle C Code for ROM patching"""
        try:
            # Write C code to temp file
            input_text = app.inputCode.get("1.0", "end-1c")
            with open("temp.c", "w") as temp_file:
                temp_file.write(input_text)
                
            # Set game ID and update include paths
            game_id = utils.GAME_TO_ID.get(app.selected_game, "generic")
            update_include_paths("temp.c", game_id)
            
            # Compile C to ASM
            if not compile_to_asm("temp.c"):
                return
                
            # Process symbols if game is selected
            if app.selected_game is not None:
                symbol_file_path = os.path.join(os.getcwd(), f"symbols/{game_id}.sym")
                dtkSymbolsTxtToLst(symbol_file_path, "temp.out")
                output_filename = parse_lst_file("temp.out", "temp_codewrite.out")
                asm_filename = "temp.s"
                append_codewrite_to_asm(asm_filename, "temp_codewrite.out")

            # Clean up ASM file
            asm_filename = "temp.s"
            remove_gnu_attribute(asm_filename)
            replace_bl_calls(asm_filename)
            
            # Compile ASM with GCC
            cmd = self.get_gcc_gekko_command()
            cmd.extend(["-a32", "-mbig", "-mregnames", "-mgekko", asm_filename])
            env = self._get_environment()
            
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            
            # Convert to Gecko code
            start_address = app.insertionAddress.get("1.0", "end-1c")
            gecko.convert_aout_to_gecko('a.out', start_address, 'b.out', overwrite=False)
            
            # Create Gecko code file
            with open("b.out", "r") as output_file:
                output_text = output_file.read()
                
            with open("b.txt", "w") as output_file:
                output_file.write("$CodeFusion\n" + output_text)
                
            # Process ROM
            self.process_rom(app, "b.txt")
            
        except Exception as e:
            CTkMessagebox(message=f"Error occurred: {str(e)}", title="Error", icon="warning", option_1="OK")
        finally:
            self._cleanup_files()

    def handle_geckoos_code_rom(self, app):
        """Handle Gecko OS Code for ROM patching"""
        try:
            # Create Gecko code file
            if app.selected_game is not None:
                self.add_symbols_to_temp_asm(app)
            else:
                self._create_temp_asm(app)
                
            with open("temp.asm", "r") as temp_file:
                output_text = temp_file.read()
                
            with open("b.txt", "w") as output_file:
                output_file.write("$CodeFusion\n" + output_text)
                
            # Process ROM
            self.process_rom(app, "b.txt")
            
        except Exception as e:
            CTkMessagebox(message=f"Error occurred: {str(e)}", title="Error", icon="warning", option_1="OK")
        finally:
            self._cleanup_files()