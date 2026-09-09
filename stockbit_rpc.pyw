"""Hidden RPC loop: shows Discord Rich Presence while Stockbit Desktop runs.

Reads presence text from the config saved by the GUI
(``%APPDATA%\\StockbitDiscordPresence\\config.json``) every tick.
"""

from backend.presence import run_forever

if __name__ == "__main__":
    run_forever()
