# ============================================
# CodeFusion
# Author: Nayla Hanegan (naylahanegan@gmail.com)
# Date: 9/23/2024
# License: MIT
# ============================================

import tkinter as tk
from tkinter import scrolledtext, StringVar
import subprocess
import queue
import threading
import os
import subprocess
import customtkinter
import version
import platform
import credits
from CTkMessagebox import CTkMessagebox
from CTkToolTip import *

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("CodeFusion")
        self.geometry("1330x780")

        # configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.create_sidebar()
        self.appFrame = None
        
        # set default values
        self.n64_button.configure(state="disabled")
        self.appFrame = self.create_n64()
        self.appFrame.grid(row=0, column=1, padx=0, pady=0, rowspan=3, sticky="nsew")

    def create_sidebar(self):
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(3, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="CodeFusion", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.n64_button = customtkinter.CTkButton(self.sidebar_frame, text="Nintendo 64", command=self.n64_view)
        self.n64_button.grid(row=1, column=0, padx=20, pady=10)

        self.gcn_wii_button = customtkinter.CTkButton(self.sidebar_frame, text="GameCube / Wii", command=self.gcn_wii_view)
        self.gcn_wii_button.grid(row=2, column=0, padx=20, pady=10)

        self.credits_button = customtkinter.CTkButton(self.sidebar_frame, text="Credits", command=self.credits_view)
        self.credits_button.grid(row=4, column=0, padx=20, pady=10)
        
        self.version_label = customtkinter.CTkLabel(self.sidebar_frame, text=version.appVersion, anchor="w", font=("Arial", 18, "bold"))
        self.version_label.grid(row=5, column=0, padx=20, pady=(10, 5))

    def n64_view(self):
        self.update_button_states("n64")
        self.create_game_frame("Nintendo 64")

    def gcn_wii_view(self):
        self.update_button_states("gcn_wii")
        self.create_game_frame("GameCube / Wii")

    def credits_view(self):
        self.update_button_states("credits")
        self.create_game_frame("Credits")

    def update_button_states(self, active_button):
        buttons = {"n64": self.n64_button, "gcn_wii": self.gcn_wii_button, "credits": self.credits_button}
        for button_name, button in buttons.items():
            button.configure(state="disabled" if button_name == active_button else "normal")

    def reset_game_frames(self):
        if self.appFrame:
            self.appFrame.destroy()

    def create_game_frame(self, game_name):
        self.reset_game_frames()
        frame_creators = {
            "Nintendo 64": self.create_n64,
            "GameCube / Wii": self.create_gcn_wii,
            "Credits": self.create_credits
        }
        creator = frame_creators.get(game_name)
        if creator:
            self.appFrame = creator()
            self.appFrame.grid(row=0, column=1, padx=0, pady=0, rowspan=3, sticky="nsew")
        else:
            print(f"Error: Unknown game frame '{game_name}'")

    def create_credits(self):
        frame = customtkinter.CTkFrame(self, fg_color=("#fcfcfc", "#2e2e2e"))
        tabview = customtkinter.CTkTabview(frame, width=2000, height=650, fg_color=("#fcfcfc", "#323232"))
        tabview.pack(padx=20, pady=20)
        
        for tab_name in ["Credits", "About", "License"]:
            tabview.add(tab_name)
            content_func = getattr(credits, f"get_{tab_name.lower()}_text", lambda: "")
            content = customtkinter.CTkLabel(tabview.tab(tab_name), width=80, height=20, text=content_func())
            content.pack(padx=10, pady=10)
        
        tabview.set("About")
        return frame

    def create_n64(self):
        frame = customtkinter.CTkFrame(self, fg_color=("#fcfcfc", "#2e2e2e"))

        return frame

    def create_gcn_wii(self):
        self.gcn_wii_frame = customtkinter.CTkFrame(self, fg_color=("#fcfcfc", "#2e2e2e"))
        
        # Input File selection
        input_label = customtkinter.CTkLabel(self.gcn_wii_frame, text="Input: ", font=("Arial", 18, "bold"))
        input_label.place(x=20, y=20)

        self.input_file_var = StringVar(value="C")
        options = ["C", "PowerPC ASM", "GeckoOS Code"]

        input_frame = customtkinter.CTkFrame(self.gcn_wii_frame, fg_color="transparent")
        input_frame.place(x=120, y=20)

        for i, option in enumerate(options):
            radio_button = customtkinter.CTkRadioButton(
                input_frame,
                text=option,
                variable=self.input_file_var,
                value=option,
                font=("Arial", 14),
                width=0,
                height=28,
                command=self.toggle_insertion_address
            )
            radio_button.pack(side="left", padx=(0, 25))
        
        # Output selection
        output_label = customtkinter.CTkLabel(self.gcn_wii_frame, text="Output: ", font=("Arial", 18, "bold"))
        output_label.place(x=20, y=60)

        self.output_var = StringVar(value="GeckoOS Code")
        output_options = ["GeckoOS Code", "Patched ROM", "XDelta Patch"]

        output_frame = customtkinter.CTkFrame(self.gcn_wii_frame, fg_color="transparent")
        output_frame.place(x=120, y=60)

        for option in output_options:
            radio_button = customtkinter.CTkRadioButton(
                output_frame,
                text=option,
                variable=self.output_var,
                value=option,
                font=("Arial", 14),
                width=0,
                height=28,
                command=self.toggle_insertion_address
            )
            radio_button.pack(side="left", padx=(0, 25))
        
        # Insertion Address input
        self.label1 = customtkinter.CTkLabel(self.gcn_wii_frame, text="Insertion Address:", font=("Arial", 14, "bold"))
        self.label1.grid(row=2, column=0, sticky="w", padx=20, pady=(100, 0))
        self.insertionAddress = customtkinter.CTkTextbox(self.gcn_wii_frame, height=20)
        self.insertionAddress.grid(row=3, column=0, padx=20, sticky="nsew")
        
        # Codes input
        self.label2 = customtkinter.CTkLabel(self.gcn_wii_frame, text="C Code:", font=("Arial", 14, "bold"))
        self.label2.grid(row=4, column=0, sticky="w", padx=20, pady=(20, 0))
        self.inputCode = customtkinter.CTkTextbox(self.gcn_wii_frame, height=100)
        self.inputCode.grid(row=5, column=0, padx=20, sticky="nsew")
        
        # Output display
        self.label3 = customtkinter.CTkLabel(self.gcn_wii_frame, text="GeckoOS Code:", font=("Arial", 14, "bold"))
        self.label3.grid(row=2, column=1, sticky="w", padx=20, pady=(100, 0))
        self.output = customtkinter.CTkTextbox(self.gcn_wii_frame, height=200)
        self.output.grid(row=3, column=1, rowspan=3, padx=20, sticky="nsew")

        # Patch button
        self.patchButton = customtkinter.CTkButton(self.gcn_wii_frame, text="Patch", command=self.patch)
        self.patchButton.grid(row=6, column=0, columnspan=2, pady=20)


        # Configure grid
        self.gcn_wii_frame.grid_columnconfigure(1, weight=1)
        self.gcn_wii_frame.grid_rowconfigure(5, weight=1)


        # Call this at the end of create_gcn_wii to set initial visibility
        self.toggle_insertion_address()

        return self.gcn_wii_frame

    def toggle_insertion_address(self):
        if self.input_file_var.get() == "GeckoOS Code":
            self.label1.grid_remove()
            self.insertionAddress.grid_remove()
            # Move Codes section up
            self.label2.grid_configure(row=2, pady=(100, 0))
            self.inputCode.grid_configure(row=3)
            # Adjust Output section
            self.label3.grid_configure(row=2)
            self.output.grid_configure(row=3, rowspan=1)
            # Make the Codes input box expand
            self.gcn_wii_frame.grid_rowconfigure(3, weight=1)
            self.gcn_wii_frame.grid_rowconfigure(5, weight=0)
        else:
            self.label1.grid()
            self.insertionAddress.grid()
            # Move Codes section back down
            self.label2.grid_configure(row=4, pady=(20, 0))
            self.inputCode.grid_configure(row=5)
            # Adjust Output section
            self.label3.grid_configure(row=2)
            self.output.grid_configure(row=3, rowspan=3)
            # Reset row configurations
            self.gcn_wii_frame.grid_rowconfigure(3, weight=0)
            self.gcn_wii_frame.grid_rowconfigure(5, weight=1)

        if self.output_var.get() != "GeckoOS Code":
            self.label3.grid_remove()
            self.output.grid_remove()
        else:
            self.label3.grid_configure(row=2, column=1, sticky="w", padx=20, pady=(100, 0))
            self.output.grid_configure(row=3, column=1, rowspan=3, padx=20, sticky="nsew")

        if self.input_file_var.get() == "PowerPC ASM":
            self.label2.configure(text="PowerPC ASM:")
        elif self.input_file_var.get() == "GeckoOS Code":
            self.label2.configure(text="GeckoOS Code:")
        else:
            self.label2.configure(text="C Code:")

        # Force the frame to update its layout
        self.update_idletasks()
    
    def patch(self):
        if self.input_file_var.get() == "GeckoOS Code" and self.output_var.get() == "GeckoOS Code":
            input_text = self.inputCode.get("1.0", "end-1c")  # Get text from input textbox
            self.output.delete("1.0", "end")  # Clear output textbox
            self.output.insert("1.0", input_text)  # Insert text into output textbox
        
        if self.input_file_var.get() == "PowerPC ASM" and self.output_var.get() == "GeckoOS Code":
            input_text = self.inputCode.get("1.0", "end-1c")  # Get text from input textbox
            
            # Save input text to temp.asm
            with open("temp.asm", "w") as temp_file:
                temp_file.write(input_text)
            
            subprocess.run(["dependenices/codewrite/powerpc-gekko-as.exe", "-a32", "-mbig", "-mregnames", "-mgekko", "temp.asm"])  # Run the external program

            # Read the output from temp.code
            with open("a.out", "r") as output_file:
                output_text = output_file.read()
            
            self.output.delete("1.0", "end")  # Clear output textbox
            self.output.insert("1.0", output_text)  # Insert text into output textbox
            
            # Clean up temporary files
            os.remove("temp.asm")
            os.remove("a.out")

        CTkMessagebox(message="Patched successfully.", title="Sucesss", icon="check", option_1="OK")

if __name__ == "__main__":
    app = App()
    app.mainloop()