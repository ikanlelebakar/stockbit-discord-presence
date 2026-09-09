"""Discord Rich Presence loop, driven by the saved config file.

The GUI owns settings; this module owns the single pypresence connection.
"""

import sys
import time
from frontend.config import load_config
from system_probes import STOCKBIT_PROCESS_NAME, is_process_running

CLIENT_ID = "1546369679885344809"
LARGE_IMAGE_KEY = "stockbit_logo_-_light_-_5389x2048_-_zonalogo_com_4_"


def build_payload(config: dict, start: float) -> dict:
    return {
        "state": config["state"],
        "details": config["details"],
        "large_text": config["large_text"],
        "large_image": LARGE_IMAGE_KEY,
        "start": start,
    }


class PresenceController:
    """State machine over one pypresence client.

    - Stockbit absent: nothing connected.
    - Stockbit present: connect once, update only when the payload changes,
      keep ``start`` stable so Discord's play time never resets.
    - Any transport failure: drop the client and retry next tick.
    """

    def __init__(self, client_factory=None, config_loader=None, is_running_probe=None):
        self._client_factory = client_factory or _default_client_factory
        self._config_loader = config_loader or load_config
        self._is_running = is_running_probe or (lambda: False)

        self._client = None
        self._connected = False
        self._last_payload = None
        self._start: float = 0.0

    def tick(self):
        config = self._config_loader()
        running = self._is_running()

        if not running:
            self._disconnect()
            return

        if not self._connected:
            self._connect()
            if not self._connected:
                return

        payload = build_payload(config, self._start)
        if payload != self._last_payload:
            try:
                self._client.update(**payload)
            except Exception as exc:
                _warn(f"presence update failed: {exc}")
                self._disconnect()
                return
            self._last_payload = payload

    def _connect(self):
        try:
            self._client = self._client_factory()
            self._client.connect()
            self._connected = True
            self._start = time.time()
            self._last_payload = None
        except Exception as exc:
            _warn(f"Discord IPC connect failed: {exc}")
            self._disconnect()

    def _disconnect(self):
        if self._client is not None:
            try:
                if self._connected:
                    self._client.clear()
                    self._client.close()
                else:
                    self._client.close()
            except Exception:
                pass
        self._client = None
        self._connected = False
        self._last_payload = None


def _default_client_factory():
    from pypresence import Presence

    return Presence(CLIENT_ID)


def _warn(message: str) -> None:
    print(f"[stockbit-rpc] {message}", file=sys.stderr)


def run_forever(
    process_name: str = STOCKBIT_PROCESS_NAME, interval: float = 5.0, ticks=None
):
    controller = PresenceController(
        is_running_probe=lambda: is_process_running(process_name)
    )
    count = 0
    while ticks is None or count < ticks:
        controller.tick()
        count += 1
        time.sleep(interval)
