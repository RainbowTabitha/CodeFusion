import os
import subprocess
import platform
from CTkMessagebox import CTkMessagebox
import gecko
import utils
from symbol_processor import dtkSymbolsTxtToLst, parse_lst_file

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
        symbol_file_path = os.path.join(os.path.dirname(__file__), f"../symbols/{game_id}.sym")

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

    def handle_powerpc_asm(self, app):
        if app.selected_game != None:
            self.add_symbols_to_temp_asm(app)
        else:
            input_text = app.inputCode.get("1.0", "end-1c")
            with open("temp.asm", "w") as temp_file:
                temp_file.write(input_text)

        cmd = ["../dependencies/codewrite/powerpc-gekko-as.exe"]
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
