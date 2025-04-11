# ============================================
# CodeFusion
# Author: Tabitha Hanegan (naylahanegan@gmail.com)
# Date: 4/10/2025
# License: MIT
# ============================================

import tkinter as tk
from tkinter import scrolledtext, StringVar
import subprocess
import queue
import threading
import os
import customtkinter
import version
import platform
import credits
import gecko
from CTkMessagebox import CTkMessagebox
from CTkToolTip import *
from downloadSymbols import download_symbol_files
from symbol_processor import dtkSymbolsTxtToLst, parse_lst_file
from gui import App

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

if __name__ == "__main__":
    app = App()
    app.mainloop()