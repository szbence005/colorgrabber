"""
Globális (rendszerszintű) billentyűkombináció regisztrálása.

A `keyboard` csomag Windows alatt akkor is érzékeli a lenyomást, ha az app
nincs fókuszban - erre épül az egész "bárhonnan grabbelhető szín" funkció.

Megjegyzés: a `keyboard` csomagnak Windows-on általában rendszergazdai
jogosultság kell ahhoz, hogy globálisan figyelje a billentyűzetet.
"""
import keyboard

DEFAULT_HOTKEY = "ctrl+alt+c"
SHOW_WINDOW_HOTKEY = "ctrl+alt+v"
QUIT_HOTKEY = "ctrl+alt+q"


def register_hotkey(callback, hotkey: str = DEFAULT_HOTKEY) -> None:
    """
    Regisztrálja a megadott hotkeyt, ami meghívja a callback függvényt.
    Ez nem blokkol - a `keyboard` csomag saját háttérszálon figyeli az eseményeket.
    """
    keyboard.add_hotkey(hotkey, callback)


def wait_forever() -> None:
    """Életben tartja a hotkey-figyelő szálat (ha külön szálban futtatod)."""
    keyboard.wait()
