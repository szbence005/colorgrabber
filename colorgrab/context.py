"""
Az éppen aktív (fókuszban lévő) ablak címének és a mögötte futó
alkalmazás nevének lekérése - ez kerül a mentett szín mellé, hogy
lásd, honnan (melyik programból) lett a szín lementve.
"""
import win32gui
import win32process
import psutil


def get_active_window_info() -> dict:
    """
    Visszaadja az aktív ablak címét ('window_title') és a hozzá tartozó
    folyamat nevét ('app_name'), pl. {"app_name": "chrome.exe", "window_title": "..."}.

    Ha bármi hiba történik (pl. rendszerablak, jogosultsági gond), nem dob
    kivételt - inkább "Ismeretlen"-t ad vissza, hogy ez soha ne akassza meg
    a szín mentését.
    """
    try:
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd) or "Ismeretlen ablak"
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        app_name = process.name()
    except Exception:
        window_title = "Ismeretlen ablak"
        app_name = "Ismeretlen"
    return {"app_name": app_name, "window_title": window_title}
