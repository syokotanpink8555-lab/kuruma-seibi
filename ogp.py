"""SNS・noteのリンクカード用の画像 1200x630: python ogp.py → ogp.png（build.py が docs/assets/ にコピー）"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

F = "/System/Library/Fonts/ヒラギノ角ゴシック W{}.ttc"
f = lambda w, s: ImageFont.truetype(F.format(w), s)
W, H = 1200, 630

im = Image.new("RGB", (W, H), "#1f6feb")
d = ImageDraw.Draw(im)
d.rounded_rectangle([40, 40, W - 40, H - 40], 32, fill="#ffffff")
d.text((100, 110), "🔧", font=ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 64), embedded_color=True)
d.text((190, 112), "くるま整備ノート", font=f(8, 64), fill="#1d2329")
d.text((100, 250), "車の「これ大丈夫？」を、", font=f(7, 52), fill="#1d2329")
d.text((100, 325), "整備士の目線でかんたんに。", font=f(7, 52), fill="#1d2329")
d.text((100, 460), "警告灯の意味・消耗品の交換時期・オイル交換・車検費用", font=f(5, 32), fill="#5b6570")
d.text((100, 510), "seibi-note.com", font=f(6, 30), fill="#1f6feb")
im.save(Path(__file__).parent / "ogp.png")
print("ok")
