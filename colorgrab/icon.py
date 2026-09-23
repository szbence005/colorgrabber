"""
Egy stilizált "színpipetta" (eyedropper) ikon megrajzolása kódból, PIL-lel.
Ugyanez a függvény adja a tálcaikont futás közben, és ebből generáljuk
a build-eléshez szükséges .ico fájlt is (lásd build_icon.py).
"""
from PIL import Image, ImageDraw


def make_icon(size: int = 256) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Sötét, lekerekített négyzet háttér (jól látszik világos és sötét tálcán is)
    pad = size * 0.04
    draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=size * 0.22,
        fill=(24, 26, 32, 255),
    )

    # A pipetta teste - vastag átlós vonal, lekerekített véggel
    body_color = (214, 217, 222, 255)
    tip = (size * 0.32, size * 0.74)     # a hegye (lent-balra) - ide "szívja" a színt
    top = (size * 0.70, size * 0.32)     # a teteje (fent-jobbra)
    width = size * 0.115

    draw.line([tip, top], fill=body_color, width=int(width))
    r = width / 2
    draw.ellipse([top[0] - r, top[1] - r, top[0] + r, top[1] + r], fill=body_color)

    # A "nyomógomb" / gumibulb a tetején
    bulb_r = size * 0.095
    bx, by = size * 0.76, size * 0.26
    draw.ellipse([bx - bulb_r, by - bulb_r, bx + bulb_r, by + bulb_r], fill=(160, 164, 172, 255))

    # A színcsepp a hegyén - ez adja a "colorful" karaktert az ikonnak
    drop_r = size * 0.10
    dx, dy = tip
    draw.ellipse([dx - drop_r, dy - drop_r, dx + drop_r, dy + drop_r], fill=(46, 138, 230, 255))
    # apró fényfolt a csepp tetején, hogy "üvegesnek" tűnjön
    hl_r = drop_r * 0.45
    draw.ellipse(
        [dx - hl_r - drop_r * 0.3, dy - hl_r - drop_r * 0.3, dx + hl_r - drop_r * 0.3, dy + hl_r - drop_r * 0.3],
        fill=(255, 255, 255, 160),
    )

    return img
