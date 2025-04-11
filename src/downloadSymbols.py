# ============================================
# CodeFusion
# Author: Tabitha Hanegan (naylahanegan@gmail.com)
# Date: 4/10/2025
# License: MIT
# ============================================

import os
import requests

# Mapping of game IDs to their symbol file URLs
SYMBOL_URL_MAPPING = {
    "GMPE01_00": "https://raw.githubusercontent.com/mariopartyrd/marioparty4/refs/heads/main/config/GMPE01_00/symbols.txt",
    "GMPE01_01": "https://raw.githubusercontent.com/mariopartyrd/marioparty4/refs/heads/main/config/GMPE01_01/symbols.txt",
    "GP5E01": "https://raw.githubusercontent.com/mariopartyrd/marioparty5/refs/heads/main/config/GP5E01/symbols.txt",
    "GP6E01": "https://raw.githubusercontent.com/mariopartyrd/marioparty6/refs/heads/main/config/GP6E01/symbols.txt",
    "GP7E01": "https://raw.githubusercontent.com/mariopartyrd/marioparty7/refs/heads/main/config/GP7E01/symbols.txt",
}

def download_symbol_files(game_id: str) -> bool:
    """
    Downloads the symbol files for the given game identifier.

    Parameters:
    - game_id (str): The identifier or name of the game.

    Returns:
    - bool: True if the download succeeded, False otherwise.
    """
    if game_id not in SYMBOL_URL_MAPPING:
        print(f"Error: No symbol file URL found fo`r game ID {game_id}")
        return False

    symbol_dir = os.path.join("../symbols")
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