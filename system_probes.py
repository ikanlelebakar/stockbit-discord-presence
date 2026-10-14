"""Local dependency probes shared by the GUI and the RPC loop."""

import os
import re
import unicodedata

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

_TICKER_RE = re.compile(r"\b([A-Z]{4})\b")
_IDLE_AFTER_SECONDS = 300.0

def extract_ticker(title: str) -> str | None:
    """Return the ticker from a Stockbit order-dialog title.

    Only the `` • TICKER`` pattern (e.g. ``Buy • BBCA``) is trusted; the main window title carries no signal.
    """
    if "•" not in title:
        return None
    match = _TICKER_RE.search(unicodedata.normalize("NFKC", title))
    return match.group(1) if match else None


def stockbit_activity(idle_after_seconds: float = _IDLE_AFTER_SECONDS) -> dict:
    """Read Stockbit window titles into a focus/ticker/idle snapshot.

    Windows-only; every Win32 call is guarded and degrades to ``{"running": ...}``. Never touches accounts.
    """
    import sys

    if sys.platform != "win32":
        return {"running": is_stockbit_running()}
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        titles: list[str] = []

        @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        def _enum_proc(hwnd, _lparam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if 0 < length < 256:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    pid = wintypes.DWORD()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    try:
                        if psutil.Process(pid.value).name().lower() == STOCKBIT_PROCESS_NAME.lower():
                            titles.append(buf.value)
                    except psutil.Error:
                        pass
            return True

        user32.EnumWindows(_enum_proc, 0)
        if not titles:
            return {"running": is_process_running(STOCKBIT_PROCESS_NAME)}

        ticker = next((t for t in (extract_ticker(x) for x in titles) if t), None)
        foreground = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(foreground)
        focused = False
        if 0 < length < 256:
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(foreground, buf, length + 1)
            focused = buf.value in titles

        idle_seconds: float | None = None
        try:
            kernel32 = ctypes.windll.kernel32

            class _LastInput(ctypes.Structure):
                _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]

            info = _LastInput(ctypes.sizeof(_LastInput), 0)
            if user32.GetLastInputInfo(ctypes.byref(info)):
                idle_seconds = (kernel32.GetTickCount() - info.dwTime) / 1000.0
        except (OSError, ValueError, OverflowError):
            idle_seconds = None

        return {
            "running": True,
            "focused": focused,
            "ticker": ticker,
            "idle": idle_seconds is not None and idle_seconds >= idle_after_seconds,
        }
    except Exception:
        try:
            return {"running": is_process_running(STOCKBIT_PROCESS_NAME)}
        except Exception:
            return {"running": False}
