import os, random, whisper, shutil
from groq import Groq
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import VideoFileClip, VideoClip

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

FONT_BOLD   = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_ITALIC = "/System/Library/Fonts/NewYorkItalic.ttf"

def transcribe_video(path):
    print("🎙️  Транскрибую...", flush=True)
    model = whisper.load_model("base")
    result = model.transcribe(path, word_timestamps=True, language="ru")
    words = []
    for seg in result.get("segments", []):
        for w in seg.get("words", []):
            words.append({"word": w["word"].strip(), "start": w["start"], "end": w["end"]})
    transcript = " ".join(w["word"] for w in words)
    print(f"✅  Знайдено {len(words)} слів")
    return words, transcript

def generate_hooks(transcript):
    print("🤖  Генерую хуки...", flush=True)
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"""Ты эксперт по вирусному контенту TikTok/Reels.
Сгенерируй 6 РАЗНЫХ хуков на РУССКОМ языке для этого видео.
Каждый хук — 2-4 слова, максимально цепляющий, эмоциональный.
Стили: вопрос, шок, призыв, провокация, обещание, тайна.
Только хуки, по одному на строку, без нумерации и знаков:
{transcript}"""}],
            max_tokens=200
        )
        hooks = [h.strip() for h in resp.choices[0].message.content.strip().split("\n") if h.strip()][:6]
        while len(hooks) < 6:
            hooks.append("СМОТРИ ДО КОНЦА")
        print(f"✅  Хуки: {hooks}")
        return hooks
    except Exception as e:
        print(f"⚠️  Помилка: {e}")
        return ["ЭТО ИЗМЕНИТ ВСЁ","НИКТО НЕ ЗНАЕТ","ТЫ ДОЛЖЕН ЗНАТЬ","СТОП ЛИСТАЙ","ПРАВДА ЛИ ЭТО","СМОТРИ ДАЛЬШЕ"]

def load_font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except:
        return ImageFont.truetype(path, size)

def outline(draw, text, x, y, font, fill, size=5):
    for dx in range(-size, size+1):
        for dy in range(-size, size+1):
            if dx*dx+dy*dy <= size*size:
                draw.text((x+dx, y+dy), text, font=font, fill=(0,0,0,255))
    draw.text((x, y), text, font=font, fill=fill)

def cx(draw, text, font, w):
    bb = draw.textbbox((0,0), text, font=font)
    return (w - (bb[2]-bb[0])) // 2

def make_text_frame(word, w, h, style):
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    text = word.upper()

    if style == 0:
        f = load_font(FONT_BOLD, 130, index=1)
        outline(draw, text, cx(draw,text,f,w), h//2-70, f, (255,255,255,255), 6)

    elif style == 1:
        f1 = load_font(FONT_BOLD, 115, index=1)
        outline(draw, text, cx(draw,text,f1,w), h//2-65, f1, (255,230,0,255), 6)

    elif style == 2:
        f = load_font(FONT_ITALIC, 105)
        outline(draw, text, cx(draw,text,f,w), h-230, f, (255,255,255,255), 5)

    elif style == 3:
        f = load_font(FONT_BOLD, 115, index=1)
        bb = draw.textbbox((0,0), text, font=f)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        x = (w-tw)//2
        y = h//2-60
        pad = 18
        draw.rectangle([x-pad, y-pad, x+tw+pad, y+th+pad], fill=(220,30,30,220))
        draw.text((x, y), text, font=f, fill=(255,255,255,255))

    elif style == 4:
        f = load_font(FONT_BOLD, 120, index=1)
        outline(draw, text, cx(draw,text,f,w), h//2-65, f, (100,255,200,255), 5)

    elif style == 5:
        words_list = text.split()
        f_s = load_font(FONT_ITALIC, 60)
        f_b = load_font(FONT_BOLD, 125, index=1)
        l1 = words_list[0] if words_list else text
        l2 = " ".join(words_list[1:]) if len(words_list)>1 else text
        outline(draw, l1, cx(draw,l1,f_s,w), h//2-90, f_s, (200,200,200,200), 3)
        outline(draw, l2, cx(draw,l2,f_b,w), h//2-20, f_b, (255,150,0,255), 6)

    return np.array(img)

def zoom_frame(frame, scale=1.06):
    h, w = frame.shape[:2]
    new_h, new_w = int(h*scale), int(w*scale)
    img = Image.fromarray(frame).resize((new_w, new_h), Image.LANCZOS)
    x = (new_w-w)//2
    y = (new_h-h)//2
    return np.array(img)[y:y+h, x:x+w]

def glitch_frame(frame, intensity=12):
    img = Image.fromarray(frame)
    r, g, b = img.split()
    shift = random.randint(3, intensity)
    w, h = img.size
    r_new = Image.new("L", (w,h), 0)
    r_new.paste(r.crop((shift,0,w,h)), (0,0))
    result = Image.merge("RGB", [r_new, g, b])
    for _ in range(random.randint(2,4)):
        y = random.randint(0, h-1)
        line = result.crop((0,y,w,y+1))
        dx = random.randint(-intensity, intensity)
        tmp = Image.new("RGB", (w,1), (0,0,0))
        tmp.paste(line, (max(0, min(w-line.width, dx)), 0))
        result.paste(tmp, (0,y))
    return np.array(result)

def shake_frame(frame, intensity=8):
    h, w = frame.shape[:2]
    dx = random.randint(-intensity, intensity)
    dy = random.randint(-intensity, intensity)
    img = Image.fromarray(frame)
    return np.array(img.transform(img.size, Image.AFFINE, [1,0,-dx,0,1,-dy]))

def vhs_frame(frame):
    img = Image.fromarray(frame)
    w, h = img.size
    overlay = Image.new("RGBA", (w,h), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    for y in range(0, h, random.randint(8,20)):
        draw.line([(0,y),(w,y)], fill=(0,0,0,random.randint(20,60)), width=1)
    result = Image.alpha_composite(img.convert("RGBA"), overlay)
    return np.array(result.convert("RGB"))

EFFECT_SETS = [
    ["zoom","glitch"],
    ["shake","flash"],
    ["vhs","zoom"],
    ["glitch","shake"],
    ["zoom","vhs"],
    ["flash","glitch"],
]

TRIM_STARTS = [0, 0, 0.5, 0, 0, 0.3]

def process_single_variant(input_path, output_path, words, hook, variant_idx):
    trim = TRIM_STARTS[variant_idx]
    effects = EFFECT_SETS[variant_idx]
    style = variant_idx

    clip = VideoFileClip(input_path)
    if trim > 0:
        clip = clip.subclip(trim)

    w, h = clip.size
    fps = clip.fps
    duration = clip.duration

    def make_frame(t):
        frame = clip.get_frame(t)

        # Zoom punch на початку кожного слова
        for wd in words:
            wt = wd["start"] - trim
            if 0 <= t - wt < 0.08:
                frame = zoom_frame(frame, 1.06)
                break

        if "glitch" in effects and random.random() < 0.07:
            frame = glitch_frame(frame)
        if "shake" in effects and random.random() < 0.06:
            frame = shake_frame(frame)
        if "vhs" in effects and random.random() < 0.4:
            frame = vhs_frame(frame)
        if "flash" in effects and random.random() < 0.04:
            frame = np.clip(frame.astype(int)+80, 0, 255).astype(np.uint8)

        # Субтитри
        if t < 2.5:
            text_layer = make_text_frame(hook, w, h, style)
        else:
            current_word = ""
            for wd in words:
                wt = wd["start"] - trim
                we = wd["end"] - trim
                if wt <= t <= we:
                    current_word = wd["word"]
                    break
            text_layer = make_text_frame(current_word, w, h, style) if current_word else None

        if text_layer is not None:
            alpha = text_layer[:,:,3:4] / 255.0
            rgb = text_layer[:,:,:3]
            frame = (frame * (1-alpha) + rgb * alpha).astype(np.uint8)

        return frame

    processed = VideoClip(make_frame, duration=duration)
    processed = processed.set_audio(clip.audio)
    processed.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        ffmpeg_params=["-crf","23"],
        logger=None
    )
    clip.close()
    processed.close()

def process_video(input_path, output_dir, file_id):
    os.makedirs(output_dir, exist_ok=True)
    words, transcript = transcribe_video(input_path)
    hooks = generate_hooks(transcript)
    output_paths = []

    for i in range(6):
        output_path = os.path.join(output_dir, f"{file_id}_v{i+1}.mp4")
        print(f"\n🎬  Варіант {i+1}/6 | хук: {hooks[i]}")
        try:
            process_single_variant(input_path, output_path, words, hooks[i], i)
            if os.path.exists(output_path):
                output_paths.append(output_path)
                print(f"✅  {os.path.getsize(output_path)/1024/1024:.1f}MB")
            else:
                print("❌  помилка")
        except Exception as e:
            print(f"❌  помилка: {e}")

    return output_paths

def cleanup_outputs(paths):
    for p in paths:
        if os.path.exists(p):
            os.remove(p)
