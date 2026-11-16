"""Render portfolio visuals from synthetic cards and the isolated OMR core."""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from generate_synthetic_cards import ANSWER_KEY, MEDIA, TOTAL_QUESTIONS
from omr_demo_core import classify_bubbles, correct_perspective_by_marks, grade_responses


ROOT = Path(__file__).resolve().parents[2]
INK, MUTED, BG, WHITE = "#172033", "#667085", "#F4F7FB", "#FFFFFF"
GREEN, ORANGE, MAGENTA, BLUE = "#27966F", "#E9892F", "#B84AA5", "#327FC2"


def font(kind, size):
    root = Path("C:/Windows/Fonts")
    names = {"r": ("segoeui.ttf", "arial.ttf"), "s": ("seguisb.ttf", "arialbd.ttf"),
             "b": ("segoeuib.ttf", "arialbd.ttf")}[kind]
    for name in names:
        if (root / name).exists():
            return ImageFont.truetype(str(root / name), size)
    return ImageFont.load_default()


F54, F34, F26, F22, F19, F17 = (font("b",54), font("b",34), font("s",26),
                                 font("r",22), font("s",19), font("r",17))


def read_bgr(path):
    data = np.frombuffer(path.read_bytes(), np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Could not read {path.name}")
    return image


def bgr_to_pil(image):
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def save_bgr(path, image):
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise RuntimeError(f"Could not encode {path.name}")
    path.write_bytes(encoded.tobytes())


def fit_on(canvas, image, box, pad=0):
    x1,y1,x2,y2 = box
    source = image.copy()
    source.thumbnail((x2-x1-2*pad, y2-y1-2*pad), Image.Resampling.LANCZOS)
    x = x1 + (x2-x1-source.width)//2
    y = y1 + (y2-y1-source.height)//2
    canvas.paste(source, (x,y))
    return (x,y,x+source.width,y+source.height)


def header(draw, title, subtitle, width):
    draw.text((80,55), title, font=F54, fill=INK)
    draw.text((82,128), subtitle, font=F22, fill=MUTED)
    draw.rounded_rectangle((width-350,58,width-80,106), radius=24, fill="#E7F4EE")
    text="SYNTHETIC DATA"
    bb=draw.textbbox((0,0),text,font=F19)
    draw.text((width-215-(bb[2]-bb[0])/2,72),text,font=F19,fill="#217A5C")


def panel(draw, box, label, accent):
    x1,y1,x2,y2=box
    draw.rounded_rectangle((x1+7,y1+9,x2+7,y2+9),radius=24,fill="#DFE5EF")
    draw.rounded_rectangle(box,radius=24,fill=WHITE,outline="#D5DDE9",width=2)
    draw.rounded_rectangle((x1,y1,x1+10,y2),radius=8,fill=accent)
    draw.text((x1+28,y1+20),label,font=F19,fill=accent)


def input_with_detected_points(image, points):
    marked=image.copy()
    ordered=np.int32([points[0],points[1],points[3],points[2]])
    cv2.polylines(marked,[ordered],True,(70,170,80),6,cv2.LINE_AA)
    for index,(x,y) in enumerate(points,1):
        cv2.circle(marked,(int(x),int(y)),18,(70,170,80),-1,cv2.LINE_AA)
        cv2.putText(marked,str(index),(int(x)-7,int(y)+7),cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,(255,255,255),2,cv2.LINE_AA)
    return marked


def recognition_overlay(card, recognition):
    overlay=card.copy()
    radius=max(int(recognition.geometry.radius*1.15),18)
    bgr={"green":(90,170,50),"orange":(30,145,235),
         "magenta":(180,60,190),"blue":(220,125,40),"gray":(150,150,150)}
    for question in range(1,TOTAL_QUESTIONS+1):
        selected=recognition.strong[question]
        weak=recognition.weak[question]
        centers=recognition.centers[question]
        for letter in selected:
            color=bgr["magenta"] if len(selected)>1 else bgr["green"]
            cv2.circle(overlay,centers[letter],radius,color,5,cv2.LINE_AA)
        for letter in weak:
            cv2.circle(overlay,centers[letter],radius,bgr["orange"],5,cv2.LINE_AA)
        if len(selected)>1:
            text,color="MULTIPLE",bgr["magenta"]
        elif weak and not selected:
            text,color="AMBIGUOUS",bgr["orange"]
        elif not selected:
            text,color="BLANK",bgr["blue"]
            first,last=centers["A"],centers["E"]
            cv2.rectangle(overlay,(first[0]-radius-5,first[1]-radius-5),
                          (last[0]+radius+5,last[1]+radius+5),color,4,cv2.LINE_AA)
        else:
            continue
        first=centers["A"]
        cv2.putText(overlay,f"Q{question:02d} {text}",(first[0]+210,first[1]+6),
                    cv2.FONT_HERSHEY_SIMPLEX,0.38,color,1,cv2.LINE_AA)
    return overlay


def geometry_comparison(input_image, points, corrected):
    canvas=Image.new("RGB",(2400,1500),BG); draw=ImageDraw.Draw(canvas)
    header(draw,"GEOMETRIC CORRECTION",
           "Synthetic perspective distortion · processed by isolated alignment and homography logic",2400)
    left=(70,215,1160,1390); right=(1240,215,2330,1390)
    panel(draw,left,"INPUT · PERSPECTIVE-DISTORTED",MAGENTA)
    panel(draw,right,"OUTPUT · NORMALIZED 1241 × 1754",GREEN)
    fit_on(canvas,bgr_to_pil(input_with_detected_points(input_image,points)),
           (left[0]+24,left[1]+70,left[2]-24,left[3]-28),18)
    fit_on(canvas,bgr_to_pil(corrected),(right[0]+24,right[1]+70,right[2]-24,right[3]-28),18)
    draw.text((80,1442),"Green polygon: alignment marks detected on the synthetic input.",font=F17,fill=MUTED)
    return canvas


def recognition_comparison(overlay, recognition, grade):
    canvas=Image.new("RGB",(2400,1500),BG); draw=ImageDraw.Draw(canvas)
    header(draw,"MARK RECOGNITION",
           "Actual classification on a synthetic card · no OCR or personal data",2400)
    left=(70,215,1570,1390); right=(1650,215,2330,1390)
    panel(draw,left,"DETECTED BUBBLES AND REVIEW STATES",GREEN)
    panel(draw,right,"DETECTION SUMMARY",BLUE)
    fit_on(canvas,bgr_to_pil(overlay),(left[0]+25,left[1]+70,left[2]-25,left[3]-30),16)
    x,y=1690,315
    legend=[(GREEN,"Single strong mark"),(ORANGE,"Weak / ambiguous mark"),
            (MAGENTA,"Multiple strong marks"),(BLUE,"Blank response")]
    for color,text in legend:
        draw.ellipse((x,y,x+26,y+26),fill=color); draw.text((x+45,y-2),text,font=F22,fill=INK); y+=65
    y+=35; draw.text((x,y),"Measured result",font=F26,fill=INK); y+=58
    metrics=[("Correct",grade.correct,GREEN),("Incorrect",grade.incorrect,"#C85454"),
             ("Blank",grade.blank,BLUE),("Multiple",grade.multiple,MAGENTA),
             ("Weak alerts",sum(bool(v) for v in recognition.weak.values()),ORANGE)]
    for label,value,color in metrics:
        draw.rounded_rectangle((x,y,x+500,y+55),radius=14,fill="#F5F7FA")
        draw.text((x+18,y+13),label,font=F19,fill=INK)
        draw.text((x+445,y+10),str(value),font=F26,fill=color); y+=70
    y+=30
    draw.text((x,y),"Threshold behavior",font=F26,fill=INK); y+=48
    for line in ("Strong > 0.40 ink density","Weak > 0.22 and ≤ 0.40",
                 "Weak marks are not counted as answers"):
        draw.text((x,y),line,font=F17,fill=MUTED); y+=32
    return canvas


def flow_board(input_image, marked_input, corrected, overlay, grade):
    canvas=Image.new("RGB",(2400,1500),BG); draw=ImageDraw.Draw(canvas)
    header(draw,"SYNTHETIC OMR CORRECTION FLOW",
           "Each processed stage below was produced by the isolated demonstration core",2400)
    boxes=[(60,235,1160,790),(1240,235,2340,790),(60,850,1160,1405),(1240,850,2340,1405)]
    titles=["01 · SYNTHETIC INPUT","02 · ALIGNMENT MARKS DETECTED",
            "03 · PERSPECTIVE NORMALIZED","04 · MARKS CLASSIFIED"]
    images=[input_image,marked_input,corrected,overlay]
    accents=[MAGENTA,GREEN,GREEN,BLUE]
    for box,title,img,accent in zip(boxes,titles,images,accents):
        panel(draw,box,title,accent)
        fit_on(canvas,bgr_to_pil(img),(box[0]+22,box[1]+64,box[2]-22,box[3]-22),10)
    draw.rounded_rectangle((1780,1315,2280,1375),radius=18,fill="#ECF5F1")
    draw.text((1810,1330),f"GRADE: {grade.correct}/{TOTAL_QUESTIONS} correct",font=F19,fill=GREEN)
    return canvas


def gif_frame(title,subtitle,image):
    canvas=Image.new("RGB",(1400,900),BG); draw=ImageDraw.Draw(canvas)
    draw.text((55,40),title,font=F34,fill=INK); draw.text((57,90),subtitle,font=F17,fill=MUTED)
    draw.rounded_rectangle((1110,42,1345,88),radius=22,fill="#E7F4EE")
    draw.text((1142,55),"SYNTHETIC DATA",font=F17,fill="#217A5C")
    fit_on(canvas,bgr_to_pil(image),(45,135,1355,850),20)
    return canvas


def main():
    input_image=read_bgr(MEDIA/"synthetic-card-perspective.png")
    corrected,points=correct_perspective_by_marks(input_image)
    if corrected is None:
        raise RuntimeError("Alignment-mark correction failed on the synthetic card")
    recognition=classify_bubbles(corrected,TOTAL_QUESTIONS)
    grade=grade_responses(recognition.strong,ANSWER_KEY)
    marked_input=input_with_detected_points(input_image,points)
    overlay=recognition_overlay(corrected,recognition)

    save_bgr(MEDIA/"synthetic-card-corrected.png",corrected)
    geometry_comparison(input_image,points,corrected).save(MEDIA/"geometry-correction-before-after.png",optimize=True)
    recognition_comparison(overlay,recognition,grade).save(MEDIA/"mark-detection-overlay.png",optimize=True)
    flow_board(input_image,marked_input,corrected,overlay,grade).save(MEDIA/"omr-correction-flow.png",optimize=True)

    frames=[
        gif_frame("01 · SYNTHETIC INPUT","Perspective-distorted answer sheet",input_image),
        gif_frame("02 · ALIGNMENT DETECTION","Four corner marks detected by the isolated algorithm",marked_input),
        gif_frame("03 · GEOMETRIC CORRECTION","Projective transform normalized to the reference canvas",corrected),
        gif_frame("04 · MARK RECOGNITION","Strong, weak, blank and multiple states classified",overlay),
        gif_frame("05 · GRADED RESULT",f"{grade.correct} correct · {grade.incorrect} incorrect · {grade.blank} blank · {grade.multiple} multiple",overlay),
    ]
    frames[0].save(MEDIA/"omr-demo.gif",save_all=True,append_images=frames[1:],
                   duration=[1000,1100,1100,1300,1700],loop=0,optimize=True)

    result={
        "synthetic":True,
        "processing":"isolated adaptation of original OMR algorithms",
        "detected_alignment_points":np.round(points,1).tolist(),
        "grid_rows":len(recognition.geometry.rows_y),
        "grid_radius_px":round(recognition.geometry.radius,2),
        "strong_marks":{str(q):v for q,v in recognition.strong.items() if v},
        "weak_marks":{str(q):v for q,v in recognition.weak.items() if v},
        "grade":{"correct":grade.correct,"incorrect":grade.incorrect,
                 "blank":grade.blank,"multiple":grade.multiple},
        "accuracy_claim":None,
    }
    (MEDIA/"omr-demo-results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result["grade"]))


if __name__ == "__main__":
    main()
