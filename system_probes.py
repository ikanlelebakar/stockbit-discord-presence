"""Local dependency probes shared by the GUI and the RPC loop."""

import os
import psutil

STOCKBIT_PROCESS_NAME = "Stockbit.exe"
_DISCORD_PIPE_SLOTS = 10


def is_process_running(process_name: str) -> bool:
    try:
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info.get("name")
                if name and name.lower() == process_name.lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except psutil.Error:
        return False
    return False


def is_stockbit_running() -> bool:
    return is_process_running(STOCKBIT_PROCESS_NAME)


def is_discord_running() -> bool:
    return any(
        os.path.exists(f"\\\\.\\pipe\\discord-ipc-{slot}")
        for slot in range(_DISCORD_PIPE_SLOTS)
    )
