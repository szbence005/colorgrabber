"""
Felelős azért, hogy a kurzor aktuális pozíciójában kiolvassa a képernyő
pixelszínét, és RGB / HEX formátumban visszaadja.
"""
import pyautogui


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def grab_color_at_cursor() -> dict:
    """
    Lekéri az egér aktuális pozícióját, majd az ott lévő pixel színét.

    Visszatérési érték: {"hex": str, "rgb": (r, g, b), "x": int, "y": int}
    """
    x, y = pyautogui.position()
    # pyautogui.pixel egy 1x1-es screenshotot csinál az adott koordinátán
    rgb = pyautogui.pixel(x, y)  # (r, g, b)
    return {
        "hex": rgb_to_hex(rgb),
        "rgb": rgb,
        "x": x,
        "y": y,
    }
