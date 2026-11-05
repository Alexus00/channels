"""Covers for Gattouz0 cam clips: hook text, stranger cam, streamer cam, red badge, #GATTOUZ0 footer."""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.normpath(os.path.join(D, "..", "fonts", "Montserrat.ttf"))
W, H = 1080, 1920
YEL, WHT, RED, GRY = (255, 229, 0), (255, 255, 255), (255, 48, 48), (210, 210, 210)
OUT = "/home/user/shorts/gattouz"
TOP, BOT = (8, 58, 670, 447), (8, 590, 670, 447)


def grab(src, t):
    out = os.path.join(D, "work", f"cov_{src}_{t}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", os.path.join(D, "src", f"{src}.mp4"),
                    "-frames:v", "1", "-vf", "scale=1920:1080", out], check=True)
    return Image.open(out).convert("RGB")


def cam(img, box, h=640):
    x, y, w, hh = box
    c = img.crop((x, y, x + w, y + hh)).resize((W, round(W * hh / w)), Image.LANCZOS)
    top = (c.height - h) // 2
    c = c.crop((0, top, W, top + h)).filter(ImageFilter.UnsharpMask(radius=3, percent=110, threshold=2))
    return ImageEnhance.Contrast(ImageEnhance.Color(c).enhance(1.15)).enhance(1.08)


def cover(name, src, t_top, t_bot, l1, l2, b1, b2):
    a, b = grab(src, t_top), grab(src, t_bot)
    bg = Image.new("RGB", (W, H), (12, 12, 14))
    d = ImageDraw.Draw(bg)

    def text(yy, s, size, fill, stroke=12):
        fnt = ImageFont.truetype(FONT, size)
        while d.textlength(s, font=fnt) > W - 60:
            size -= 4; fnt = ImageFont.truetype(FONT, size)
        tw = d.textlength(s, font=fnt)
        d.text(((W - tw) / 2 + 6, yy + 8), s, font=fnt, fill=(0, 0, 0), stroke_width=stroke, stroke_fill=(0, 0, 0))
        d.text(((W - tw) / 2, yy), s, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))

    bg.paste(cam(a, TOP), (0, 330)); bg.paste(cam(b, BOT), (0, 1000))
    d.rectangle((0, 322, W, 330), fill=YEL); d.rectangle((0, 1640, W, 1648), fill=YEL)
    d.rectangle((0, 970, W, 1000), fill=(12, 12, 14))
    text(60, l1, 100, WHT); text(190, l2, 100, YEL)
    text(1665, b1 + " " + b2, 130, RED, stroke=14)
    text(H - 70, "#GATTOUZ0", 36, GRY, stroke=5)
    p = os.path.join(OUT, name + "_cover.jpg"); bg.save(p, quality=93)
    return p


C = {
 "monkeys": ("gattouz_pet_monkeys", "clip_01M6CC7M92F7JW8P27YKJS6W97", 57.6, 102.5, "HE SHOWED A STRANGER", "HIS PET MONKEYS...", "MEET THE", "MONKEYS"),
 "lookalike": ("gattouz_lookalike_son", "cr_lookalike", 52.6, 47.6, "GATTOUZ0 MATCHED", "WITH HIS LOOKALIKE", "HELLO", "SON?!"),
 "fans": ("gattouz_fans_cant_believe", "cr_fans2", 13.2, 12.6, "STRANGERS CAN'T BELIEVE", "IT'S GATTOUZ0...", "IS THIS", "REAL?!"),
 "belike": ("gattouz_can_i_be_like_you", "cr_dab", 52.3, 55.0, "\"CAN I BE", "LIKE YOU?\"", "HIS", "ANSWER..."),
}
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for k in sys.argv[1:] or C:
        n, *a = C[k]; print(cover(n, *a))
