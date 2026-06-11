import sys, os, json, shutil, subprocess, requests
from groq import Groq
from dotenv import load_dotenv
import whisper

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
PEXELS_KEY = "s5U1lsRF7d5tOZbyqJ75hsydYUxiyd0eOqRjmMzRJaxqWI0oe3wTgAYM"

BASE = os.path.expanduser("~/Library/CloudStorage/GoogleDrive-martintrade777@gmail.com/Мій диск/VideoBot")
RAW_DIR = os.path.join(BASE, "raw")
DONE_DIR = os.path.join(BASE, "done")
REMOTION_DIR = os.path.expanduser("~/Downloads/remotion_bot")
REMOTION_PUBLIC = os.path.join(REMOTION_DIR, "public")

DESTINATIONS = [
    os.path.join(BASE, "ready/Instagram/Акк1"),
    os.path.join(BASE, "ready/Instagram/Акк2"),
    os.path.join(BASE, "ready/TikTok/Акк1"),
    os.path.join(BASE, "ready/TikTok/Акк2"),
    os.path.join(BASE, "ready/YouTube/Акк1"),
    os.path.join(BASE, "ready/YouTube/Акк2"),
]

PLATFORMS = [
    ("Instagram", "Акк1"),
    ("Instagram", "Акк2"),
    ("TikTok", "Акк1"),
    ("TikTok", "Акк2"),
    ("YouTube", "Акк1"),
    ("YouTube", "Акк2"),
]

STYLES = [0, 1, 2, 3, 4, 5]


def send_tg(text):
    import urllib.request, urllib.parse
    url = "https://api.telegram.org/bot8857862098:AAERoVN9gEq6abPj5qAOGJM_lU6iu7rXyK4/sendMessage"
    data = urllib.parse.urlencode({"chat_id": "5488407395", "text": text}).encode()
    try:
        urllib.request.urlopen(url, data)
    except Exception as e:
        print("TG помилка: " + str(e))


def send_tg_with_description(video_name, platform, account, transcript, variant):
    try:
        tips = {
            "Instagram": "3-4 рядки + 15-20 хештегів",
            "TikTok": "1-2 рядки + 5-7 хештегів",
            "YouTube": "5-6 рядків + 10-15 хештегів + SEO теги через кому",
        }
        styles = ["питання до глядача", "шокуючий факт", "особиста історія", "провокація", "корисна порада", "заклик"]
        prompt = (
            "Ти SMM трейдера який навчає людей торгівлі. Напиши опис для " + platform +
            " (" + tips.get(platform, "") + "). Стиль: " + styles[variant % 6] +
            ". Мова: РУССКИЙ. Перші 2 рядки чіпляючі та інтригуючі. " +
            "Органічно додай: Всё объясняю в профиле 👆. " +
            "НЕ використовуй слова: бесплатно, заработок, сигналы, прибыль, инвестиции, доход, копирование. " +
            "Хештеги без токсичних слів. Кожен раз унікальний текст. " +
            "Транскрипт відео: " + transcript
        )
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        desc = resp.choices[0].message.content.strip()
        folder_links = {
            "Instagram/Акк1": "https://drive.google.com/drive/folders/1pDdE623_3z0ANdN7yKR5jDLmiocIRJad",
            "Instagram/Акк2": "https://drive.google.com/drive/folders/1E1SMSmREbgHEucqdjH1MYvtGr2ZHtfW8",
            "TikTok/Акк1": "https://drive.google.com/drive/folders/18jkdDYXiq4r3ctjeh7OWBQoPH5EejDbG",
            "TikTok/Акк2": "https://drive.google.com/drive/folders/1KbKU7qLNCFDvVubZQuC5_flymtbVUYiS",
            "YouTube/Акк1": "https://drive.google.com/drive/folders/1sDcSyf1aXt1Iw-eGKHJ86FHzH8Z8aDO3",
            "YouTube/Акк2": "https://drive.google.com/drive/folders/1e95Fxgp94SoH1iAFcmjU69p7EXgEJA0L",
        }
        link = folder_links.get(platform + "/" + account, "")
        text = "✅ " + video_name + "\n📱 " + platform + " " + account + "\n📁 " + link + "\n\n" + desc
        import urllib.request, urllib.parse
        url = "https://api.telegram.org/bot8857862098:AAERoVN9gEq6abPj5qAOGJM_lU6iu7rXyK4/sendMessage"
        data = urllib.parse.urlencode({"chat_id": "5488407395", "text": text}).encode()
        urllib.request.urlopen(url, data)
        print("TG: " + platform + " " + account + " відправлено")
    except Exception as e:
        print("TG помилка: " + str(e))


def transcribe(path):
    print("Транскрибую...", flush=True)
    model = whisper.load_model("base")
    result = model.transcribe(path, word_timestamps=True, language="ru")
    words = []
    for seg in result.get("segments", []):
        for w in seg.get("words", []):
            words.append({"word": w["word"].strip(), "start": w["start"], "end": w["end"]})
    transcript = " ".join(w["word"] for w in words)
    print("OK " + str(len(words)) + " слів")
    return words, transcript


def generate_hooks(transcript):
    print("Генерую хуки...", flush=True)
    prompt = (
        "Ты эксперт по вирусному контенту TikTok и Reels про трейдинг, деньги и мотивацию. "
        "Создай 6 РАЗНЫХ цепляющих хуков на РУССКОМ для этого видео. "
        "Каждый хук использует РАЗНЫЙ психологический триггер:\n"
        "1. Шок/провокация (например: Это уничтожит твой депозит)\n"
        "2. Тайна/интрига (например: Никто не говорит об этом)\n"
        "3. Личная боль (например: Я потерял всё из-за этого)\n"
        "4. Обещание (например: После этого всё изменится)\n"
        "5. Вопрос (например: Почему богатые молчат об этом?)\n"
        "6. Срочность (например: Запомни это прямо сейчас)\n"
        "Правила: 3-6 слов, без эмодзи, CAPS для ключевого слова, только хуки по одному на строку.\n"
        "Транскрипт: " + transcript
    )
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    hooks = [h.strip() for h in resp.choices[0].message.content.strip().split("\n") if h.strip() and len(h.strip()) > 3][:6]
    while len(hooks) < 6:
        hooks.append("ЭТО ИЗМЕНИТ ВСЁ")
    print("Хуки: " + str(hooks))
    return hooks


def generate_brolls(transcript, duration):
    print("Генерую B-roll...", flush=True)
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Для транскрипту згенеруй 4 B-roll вставки. ТІЛЬКИ JSON масив без зайвого: [{\"keyword\": \"money\", \"time\": 1.5}]. Відео " + str(round(duration)) + " сек. Прості англійські слова.\nТранскрипт: " + transcript}],
        max_tokens=200
    )
    raw = resp.choices[0].message.content
    data = json.loads(raw[raw.find("["):raw.rfind("]")+1])
    brolls = []
    for item in data:
        r = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": item["keyword"], "per_page": 3, "orientation": "portrait"}
        )
        for v in r.json().get("videos", []):
            for f in v["video_files"]:
                if f["quality"] == "hd":
                    brolls.append({"keyword": item["keyword"], "time": item["time"], "url": f["link"]})
                    break
            break
    print("OK " + str(len(brolls)) + " B-roll")
    return brolls


def get_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True
    )
    return float(r.stdout.strip())


def convert_video(src, dst):
    subprocess.run([
        "ffmpeg", "-i", src,
        "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.0",
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        dst, "-y"
    ], capture_output=True)


def write_root(name, words, hook, style, brolls, frames):
    words_str = json.dumps(words, ensure_ascii=False)
    brolls_str = json.dumps(brolls, ensure_ascii=False)
    hook_clean = hook.replace('"', '\\"')
    content = "import {Composition, staticFile} from 'remotion';\n"
    content += "import {VideoComposition} from './VideoComposition';\n"
    content += "export const RemotionRoot: React.FC = () => {\n"
    content += "  return (\n    <>\n"
    content += "      <Composition\n"
    content += "        id=\"VideoBot\"\n"
    content += "        component={VideoComposition}\n"
    content += "        durationInFrames={" + str(frames) + "}\n"
    content += "        fps={30}\n"
    content += "        width={1080}\n"
    content += "        height={1920}\n"
    content += "        defaultProps={{\n"
    content += "          videoSrc: staticFile(\"" + name + ".mp4\"),\n"
    content += "          words: " + words_str + ",\n"
    content += "          hook: \"" + hook_clean + "\",\n"
    content += "          style: " + str(style) + ",\n"
    content += "          inserts: [],\n"
    content += "          brolls: " + brolls_str + ",\n"
    content += "        }}\n"
    content += "      />\n    </>\n  );\n};\n"
    with open(os.path.join(REMOTION_DIR, "src", "Root.tsx"), "w") as f:
        f.write(content)


def process_video(video_path):
    name = os.path.splitext(os.path.basename(video_path))[0]
    print("\n" + "="*40 + "\n" + name + "\n" + "="*40)

    converted = os.path.join(REMOTION_PUBLIC, name + ".mp4")
    print("Конвертую...", flush=True)
    convert_video(video_path, converted)

    words, transcript = transcribe(video_path)
    hooks = generate_hooks(transcript)
    duration = get_duration(video_path)
    frames = int(duration * 30)

    for i, dest in enumerate(DESTINATIONS):
        hook = hooks[i]
        style = STYLES[i]
        out = os.path.join(dest, name + "_v" + str(i+1) + ".mp4")
        print("Варіант " + str(i+1) + "/6 | " + hook, flush=True)

        brolls = generate_brolls(transcript, duration)
        write_root(name, words, hook, style, brolls, frames)

        result = subprocess.run(
            ["npx", "remotion", "render", "VideoBot", out, "--timeout", "300000", "--concurrency", "4"],
            cwd=REMOTION_DIR, capture_output=True, text=True
        )
        if os.path.exists(out):
            size = os.path.getsize(out)/1024/1024
            print("OK " + str(round(size, 1)) + "MB")
            plat, acc = PLATFORMS[i]
            send_tg_with_description(os.path.basename(out), plat, acc, transcript, i)
        else:
            print("ПОМИЛКА: " + result.stderr[-200:])


def main():
    videos = sorted([
        os.path.join(RAW_DIR, f)
        for f in os.listdir(RAW_DIR)
        if f.lower().endswith((".mp4", ".mov")) and not f.startswith(".")
    ])
    if not videos:
        print("Немає відео в raw/")
        return
    print("Знайдено " + str(len(videos)) + " відео")
    send_tg("📥 Починаю обробку " + str(len(videos)) + " відео...")
    for v in videos:
        process_video(v)
    # Очищення public/ від конвертованих відео
    import shutil as _sh
    import glob
    for f in glob.glob(os.path.join(REMOTION_PUBLIC, "*.mp4")):
        try:
            os.remove(f)
        except:
            pass
    for f in glob.glob(os.path.join(REMOTION_PUBLIC, "lottie/broll_*.mp4")):
        try:
            os.remove(f)
        except:
            pass
    print("🧹 public/ очищено")

    for v in videos:
        done = v.replace("/raw/", "/done/")
        try:
            _sh.move(v, done)
        except Exception as e:
            print("Помилка переміщення: " + str(e))
    send_tg("✅ Готово! Відео в Google Drive → VideoBot → ready/")
    print("Готово!")


if __name__ == "__main__":
    main()
