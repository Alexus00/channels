"""Covers for the JasonTheWeen week-1 batch: top hook, face panel, 2-line badge, #JASONTHEWEEN footer."""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.normpath(os.path.join(D, "..", "fonts", "Montserrat.ttf"))
W, H = 1080, 1920
YEL, WHT, RED, GRY = (255, 229, 0), (255, 255, 255), (255, 48, 48), (210, 210, 210)
OUT = "/home/user/shorts/streamrewind"


def grab(src, t):
    out = os.path.join(D, "work", f"cov_{src}_{t}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", os.path.join(D, "src", f"hq_{src}.mp4"),
                    "-frames:v", "1", "-vf", "scale=1920:1080", out], check=True)
    return Image.open(out).convert("RGB")


def cover(name, src, t, x, l1, l2, b1, b2, ch=920, y=0):
    img = grab(src, t)
    cw = int(ch * 1215 / 1080); PH = 860
    x0 = int(min(max(x - cw // 2, 0), 1920 - cw)); hh = int(cw * PH / W)
    y0 = int(min(max(y - hh // 2, 0), 1080 - hh))
    f = img.crop((x0, y0, x0 + cw, y0 + hh)).resize((W, PH), Image.LANCZOS)
    f = f.filter(ImageFilter.UnsharpMask(radius=3, percent=120, threshold=2))
    f = ImageEnhance.Contrast(ImageEnhance.Color(f).enhance(1.2)).enhance(1.1)
    bg = img.resize((W, H)).filter(ImageFilter.GaussianBlur(30))
    bg = ImageEnhance.Brightness(bg).enhance(0.3)
    fy = 500
    bg.paste(f, (0, fy)); fh = f.height
    d = ImageDraw.Draw(bg)
    d.rectangle((0, fy - 8, W, fy), fill=YEL); d.rectangle((0, fy + fh, W, fy + fh + 8), fill=YEL)

    def text(yy, s, size, fill, stroke=12):
        fnt = ImageFont.truetype(FONT, size)
        while d.textlength(s, font=fnt) > W - 60:
            size -= 4; fnt = ImageFont.truetype(FONT, size)
        tw = d.textlength(s, font=fnt)
        d.text(((W - tw) / 2 + 6, yy + 8), s, font=fnt, fill=(0, 0, 0), stroke_width=stroke, stroke_fill=(0, 0, 0))
        d.text(((W - tw) / 2, yy), s, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))

    text(160, l1, 110, WHT); text(320, l2, 110, YEL)
    by = fy + fh + 40
    text(by, b1, 120, WHT); text(by + 150, b2, 170, RED, stroke=16)
    text(H - 110, "CONTEXT LOADING  @contextloading10", 40, GRY, stroke=5)
    p = os.path.join(OUT, name + "_cover.jpg"); bg.save(p, quality=93)
    return p



if __name__ == "__main__":
    print(cover("sr_emily_cops_scream", "emily_cops", 22.6, 1728, "EXTRAEMILY SCREAMED", "SO LOUD THE COPS...", "SHOWED", "UP?!", ch=440, y=610))
    print(cover("sr_caseoh_freestyle", "caseoh_freestyle", 19.5, 201, "CASEOH STARTED", "FREESTYLING...", "RATE IT", "1-10", ch=300, y=287))
