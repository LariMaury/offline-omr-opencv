"""Render a conceptual diagram; no original OMR algorithm is executed."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 2000, 1180
BG, INK, MUTED, WHITE = "#F5F7FB", "#172033", "#667085", "#FFFFFF"

def get_font(kind, size):
    root = Path("C:/Windows/Fonts")
    names = {"r": ("segoeui.ttf", "arial.ttf"), "s": ("seguisb.ttf", "arialbd.ttf"),
             "b": ("segoeuib.ttf", "arialbd.ttf")}[kind]
    for name in names:
        if (root / name).exists():
            return ImageFont.truetype(str(root / name), size)
    return ImageFont.load_default()

TITLE, SUB = get_font("b", 54), get_font("r", 23)
BADGE, NUM = get_font("s", 17), get_font("b", 24)
CARD, DETAIL = get_font("s", 25), get_font("r", 18)
LABEL, FOOT = get_font("s", 18), get_font("r", 17)

STAGES = [
    ("Assessment Import", "Scanned PDF", "#7756D8"),
    ("PDF Conversion", "PyMuPDF · 150 DPI", "#7756D8"),
    ("Image Preprocessing", "Grayscale · thresholding", "#168B72"),
    ("Geometric Correction", "Alignment marks · homography", "#168B72"),
    ("Mark Recognition", "Grid calibration · ink density", "#168B72"),
    ("Student Association", "OCR + optional local roster", "#2176B9"),
    ("Automated Grading", "Answer key · test variant", "#2176B9"),
    ("Indicator Calculation", "Class · subject · question", "#2176B9"),
    ("Reports", "Excel · PDF · local history", "#D97728"),
]

def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def arrow(draw, start, end):
    draw.line([start, end], fill="#8A98B3", width=5)
    x1, y1 = start; x2, y2 = end
    if abs(x2-x1) >= abs(y2-y1):
        d = 1 if x2 > x1 else -1; tip = [(x2,y2),(x2-15*d,y2-10),(x2-15*d,y2+10)]
    else:
        d = 1 if y2 > y1 else -1; tip = [(x2,y2),(x2-10,y2-15*d),(x2+10,y2-15*d)]
    draw.polygon(tip, fill="#8A98B3")

def stage_card(draw, box, number, title, detail, accent):
    x1,y1,x2,y2 = box
    rounded(draw, (x1+7,y1+9,x2+7,y2+9), 24, "#E2E7F0")
    rounded(draw, box, 24, WHITE, "#DDE3ED", 2)
    rounded(draw, (x1,y1,x1+10,y2), 8, accent)
    rounded(draw, (x1+28,y1+27,x1+72,y1+71), 13, accent)
    text = f"{number:02d}"; bb = draw.textbbox((0,0), text, font=NUM)
    draw.text((x1+50-(bb[2]-bb[0])/2, y1+49-(bb[3]-bb[1])/2-bb[1]), text, font=NUM, fill=WHITE)
    draw.text((x1+28,y1+91), title, font=CARD, fill=INK)
    draw.text((x1+28,y1+134), detail, font=DETAIL, fill=MUTED)

def render():
    image = Image.new("RGB", (W,H), BG); draw = ImageDraw.Draw(image)
    draw.text((110,78), "OFFLINE OMR PROCESSING PIPELINE", font=TITLE, fill=INK)
    draw.text((112,151), "From scanned assessment sheets to local indicators and reports", font=SUB, fill=MUTED)
    rounded(draw, (1570,78,1890,126), 24, "#E9E4FA")
    text = "CONCEPTUAL ILLUSTRATION"; bb = draw.textbbox((0,0), text, font=BADGE)
    draw.text((1730-(bb[2]-bb[0])/2,93), text, font=BADGE, fill="#6244BB")
    rounded(draw, (80,230,1920,920), 36, "#FAFBFD", "#D8DFEB", 3)
    rounded(draw, (112,252,345,292), 20, "#E8F2FC")
    draw.text((139,262), "LOCAL / OFFLINE", font=LABEL, fill="#205F91")
    top = [(130+i*354,335,450+i*354,540) for i in range(5)]
    bottom = [(1370-i*402,650,1720-i*402,855) for i in range(4)]
    for i, box in enumerate(top): stage_card(draw, box, i+1, *STAGES[i])
    for i, box in enumerate(bottom): stage_card(draw, box, i+6, *STAGES[i+5])
    for a,b in zip(top,top[1:]): arrow(draw,(a[2]+8,(a[1]+a[3])//2),(b[0]-8,(b[1]+b[3])//2))
    arrow(draw,((top[-1][0]+top[-1][2])//2,top[-1][3]+12),((bottom[0][0]+bottom[0][2])//2,bottom[0][1]-12))
    for a,b in zip(bottom,bottom[1:]): arrow(draw,(a[0]-8,(a[1]+a[3])//2),(b[2]+8,(b[1]+b[3])//2))
    rounded(draw, (210,965,1790,1035), 24, WHITE, "#C8D2E2", 2)
    draw.text((285,982), "OPTIONAL ONLINE INPUT", font=LABEL, fill="#4E5D75")
    draw.text((535,983), "Answer-key configuration only · excluded from the public visual demo", font=DETAIL, fill=MUTED)
    draw.text((112,1092), "Synthetic-data portfolio · Conceptual architecture, not an engine-generated result.", font=FOOT, fill=MUTED)
    output = Path(__file__).resolve().parents[1]/"media"/"omr-processing-flow.png"
    image.save(output, "PNG", optimize=True); print(output)

if __name__ == "__main__": render()
