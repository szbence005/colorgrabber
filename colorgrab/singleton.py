"""
Biztosítja, hogy a ColorGrabbernek egyszerre csak egy példánya fusson.

Ha a Start menüből (vagy bárhonnan) újra elindítják, miközben már fut egy
háttérbeli példány, ez a modul teszi lehetővé, hogy az új indítási kísérlet
ne egy második ablakot nyisson, hanem "szóljon" a már futó példánynak, hogy
mutassa meg magát, majd azonnal kilépjen.

Egyszerű, fájl-alapú megoldás: egy lock fájlban tároljuk a futó példány
PID-jét, egy másik fájl (signal) jelzi a "mutasd az ablakot" kérést.
"""
import os
import psutil

APP_DIR_NAME = "ColorGrabber"


def _app_dir() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, APP_DIR_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def _lock_path() -> str:
    return os.path.join(_app_dir(), "colorgrabber.lock")


def _signal_path() -> str:
    return os.path.join(_app_dir(), "show_request.signal")


def is_already_running() -> bool:
    """Megnézi, fut-e már egy másik példány (a lock fájlban lévő PID alapján)."""
    lock_path = _lock_path()
    if not os.path.exists(lock_path):
        return False
    try:
        with open(lock_path, "r") as f:
            pid = int(f.read().strip())
    except (ValueError, OSError):
        return False
    return psutil.pid_exists(pid)


def acquire_lock() -> None:
    """A jelenlegi folyamat PID-jét írja a lock fájlba - ez lesz 'a' futó példány."""
    with open(_lock_path(), "w") as f:
        f.write(str(os.getpid()))


def release_lock() -> None:
    try:
        os.remove(_lock_path())
    except OSError:
        pass


def request_show() -> None:
    """Jelzi a már futó példánynak, hogy mutassa meg az ablakát."""
    with open(_signal_path(), "w") as f:
        f.write("show")


def consume_show_request() -> bool:
    """
    Ha van függőben lévő 'mutasd az ablakot' kérés, törli azt és True-t ad
    vissza. A futó példány ezt rendszeresen lekérdezi (pollozza).
    """
    signal_path = _signal_path()
    if os.path.exists(signal_path):
        try:
            os.remove(signal_path)
        except OSError:
            pass
        return True
    return False
