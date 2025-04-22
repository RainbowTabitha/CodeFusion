# ============================================
# CodeFusion
# Author: Tabitha Hanegan (naylahanegan@gmail.com)
# Date: 4/10/2025
# License: MIT
# ============================================

import sys
import os
import requests
from utils import SYMBOL_URL_MAPPING

def download_symbol_files(game_id: str) -> bool:
    if game_id not in SYMBOL_URL_MAPPING:
        print(f"Error: No symbol file URL found for game ID {game_id}")
        return False

    # Determine the base path
    if getattr(sys, 'frozen', False):
        # If the application is frozen, use the executable's directory
        base_path = sys._MEIPASS
    else:
        # Otherwise, use the script's directory
        base_path = os.path.dirname(os.path.abspath(__file__))

    symbol_dir = os.path.join(base_path, "symbols")
    os.makedirs(symbol_dir, exist_ok=True)

    symbol_url = SYMBOL_URL_MAPPING[game_id]
    output_path = os.path.join(symbol_dir, f"{game_id}.sym")

    try:
        print(f"Downloading symbol file from {symbol_url}...")
        response = requests.get(symbol_url, timeout=10)

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print("Symbol file downloaded successfully.")
            return True
        else:
            print(f"Failed to download symbol file: HTTP {response.status_code}")
            return False

    except requests.RequestException as e:
        print(f"Request error while downloading symbol file: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False