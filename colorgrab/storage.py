"""
Egyszerű JSON-alapú tárolás a lementett színekhez.

A színek a felhasználó AppData mappájában tárolódnak, hogy az app
bármelyik könyvtárból indítva ugyanazt a fájlt találja meg.
"""
import json
import os
from datetime import datetime

APP_DIR_NAME = "ColorGrabber"
FILE_NAME = "colors.json"


def _get_storage_path() -> str:
    """Visszaadja a colors.json teljes elérési útját, és létrehozza a mappát, ha nem létezik."""
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    app_dir = os.path.join(base, APP_DIR_NAME)
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, FILE_NAME)


def load_colors() -> list[dict]:
    """Betölti a mentett színeket. Ha nincs még fájl, üres listát ad vissza."""
    path = _get_storage_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_all(colors: list[dict]) -> None:
    path = _get_storage_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(colors, f, indent=2, ensure_ascii=False)


def add_color(
    hex_value: str,
    rgb: tuple[int, int, int],
    x: int,
    y: int,
    app_name: str = "Ismeretlen",
    window_title: str = "",
) -> dict:
    """Hozzáad egy új színt a listához (a lista elejére), és elmenti a fájlba."""
    entry = {
        "hex": hex_value,
        "rgb": list(rgb),
        "x": x,
        "y": y,
        "app_name": app_name,
        "window_title": window_title,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    colors = load_colors()
    colors.insert(0, entry)
    _save_all(colors)
    return entry


def delete_color(index: int) -> None:
    """Törli a listából az adott indexű színt (a jelenlegi, mentett sorrend szerint)."""
    colors = load_colors()
    if 0 <= index < len(colors):
        colors.pop(index)
        _save_all(colors)
