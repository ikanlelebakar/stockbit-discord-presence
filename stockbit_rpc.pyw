import time
import psutil
from pypresence import Presence

CLIENT_ID = "1546369679885344809"
PROCESS_NAME = "Stockbit.exe"

rpc = None
is_running = False

def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

while True:
    stockbit_aktif = is_process_running(PROCESS_NAME)

    if stockbit_aktif and not is_running:
        try:
            rpc = Presence(CLIENT_ID)
            rpc.connect()
            rpc.update(
                state="No Risk No Ferari",
                details="Ragumu Rugimu",
                large_image="stockbit_logo_-_light_-_5389x2048_-_zonalogo_com_4_",
                large_text="Stockbit Desktop",
                start=time.time()
            )
            is_running = True
        except Exception:
            rpc = None

    elif not stockbit_aktif and is_running:
        if rpc:
            try:
                rpc.clear()
                rpc.close()
            except Exception:
                pass
            rpc = None
        is_running = False

    time.sleep(5)
