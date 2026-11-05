"""Cover generator (1080x1920): big reaction face + title + circled inset + badge."""
import os, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
FONT = os.path.join(D, "..", "fonts", "Montserrat.ttf")
YEL, WHT, RED, GRN = (255, 229, 0), (255, 255, 255), (255, 48, 48), (80, 255, 80)


def grab(clip, t):
    p = next(os.path.join(D, d, clip + ".mp4") for d in ("raw", "raw2", "raw3") if os.path.exists(os.path.join(D, d, clip + ".mp4")))
    out = os.path.join(D, "cover", f"g_{clip}_{t}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", p, "-frames:v", "1",
                    "-vf", "scale=1920:1080", out], check=True)
    return Image.open(out).convert("RGB")


def cover(out, face, inset, line1, line2, badge, accent=YEL, badge_col=RED):
    """face/inset = (clip, t, box). box is [x,y,w,h] in 1920x1080 space."""
    fimg = grab(face[0], face[1]); x, y, w, h = face[2]
    fh = round(1080 * h / w)
    f = fimg.crop((x, y, x + w, y + h)).resize((1080, fh), Image.LANCZOS)
    f = f.filter(ImageFilter.UnsharpMask(radius=3, percent=120, threshold=2))
    f = ImageEnhance.Contrast(ImageEnhance.Color(f).enhance(1.2)).enhance(1.12)

    bg = fimg.resize((W, round(W * 1080 / 1920))).resize((W, H)).filter(ImageFilter.GaussianBlur(30))
    bg = ImageEnhance.Brightness(bg).enhance(0.3)
    fy = 560
    bg.paste(f, (0, fy))
    d = ImageDraw.Draw(bg)
    d.rectangle((0, fy - 8, W, fy), fill=accent)
    d.rectangle((0, fy + fh, W, fy + fh + 8), fill=accent)

    if inset:
        iimg = grab(inset[0], inset[1]); x, y, w, h = inset[2]
        t = ImageEnhance.Brightness(iimg.crop((x, y, x + w, y + h)).resize((330, 330), Image.LANCZOS)).enhance(1.2)
        m = Image.new("L", t.size, 0); ImageDraw.Draw(m).ellipse((0, 0, 329, 329), fill=255)
        TX, TY = 700, fy + fh - 250
        bg.paste(t, (TX, TY), m)
        d.ellipse((TX - 10, TY - 10, TX + 340, TY + 340), outline=RED, width=16)
        d.line((560, TY - 40, 690, TY + 60), fill=RED, width=22)
        d.polygon([(718, TY + 82), (650, TY + 78), (690, TY + 20)], fill=RED)

    def text(yy, s, size, fill, stroke=12):
        fnt = ImageFont.truetype(FONT, size)
        while d.textlength(s, font=fnt) > W - 60: size -= 4; fnt = ImageFont.truetype(FONT, size)
        tw = d.textlength(s, font=fnt)
        d.text(((W - tw) / 2 + 6, yy + 8), s, font=fnt, fill=(0, 0, 0), stroke_width=stroke, stroke_fill=(0, 0, 0))
        d.text(((W - tw) / 2, yy), s, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))

    text(140, line1, 128, WHT)
    text(300, line2, 110, accent)
    text(fy + fh + 60, badge, 200, badge_col, stroke=16)
    bg.save(out, quality=95)
    return out
