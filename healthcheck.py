import os, subprocess, urllib.request, urllib.parse

def send_tg(text):
    url = "https://api.telegram.org/bot8857862098:AAERoVN9gEq6abPj5qAOGJM_lU6iu7rXyK4/sendMessage"
    data = urllib.parse.urlencode({"chat_id": "5488407395", "text": text}).encode()
    try:
        urllib.request.urlopen(url, data)
    except:
        pass

def check():
    problems = []
    ok = []

    # 1. Remotion сервер
    try:
        urllib.request.urlopen("http://localhost:3000", timeout=5)
        ok.append("✅ Remotion сервер")
    except:
        problems.append("❌ Remotion сервер не працює")

    # 2. Google Drive
    base = os.path.expanduser("~/Library/CloudStorage/GoogleDrive-martintrade777@gmail.com/Мій диск/VideoBot")
    if os.path.exists(base):
        ok.append("✅ Google Drive")
    else:
        problems.append("❌ Google Drive недоступний")

    # 3. raw/ папка
    raw = os.path.join(base, "raw")
    if os.path.exists(raw):
        count = len([f for f in os.listdir(raw) if f.endswith(".mp4")])
        if count > 0:
            ok.append(f"📥 В raw/ є {count} відео для обробки")
        else:
            ok.append("✅ raw/ порожній")
    else:
        problems.append("❌ raw/ папка не знайдена")

    # 4. Groq API
    try:
        from dotenv import load_dotenv
        from groq import Groq
        load_dotenv(os.path.expanduser("~/Downloads/tg_bot/.env"))
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5
        )
        ok.append("✅ Groq API")
    except Exception as e:
        problems.append("❌ Groq API: " + str(e)[:50])

    # 5. ffmpeg
    r = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    if r.returncode == 0:
        ok.append("✅ ffmpeg")
    else:
        problems.append("❌ ffmpeg не знайдено")

    # 6. Watcher процес
    r = subprocess.run(["pgrep", "-f", "watcher.py"], capture_output=True)
    if r.returncode == 0:
        ok.append("✅ Watcher працює")
    else:
        problems.append("❌ Watcher не запущений")

    # Відправляємо звіт
    if problems:
        msg = "⚠️ Healthcheck — є проблеми!\n\n"
        msg += "\n".join(problems)
        msg += "\n\n" + "\n".join(ok)
    else:
        msg = "✅ Система працює нормально\n\n" + "\n".join(ok)

    send_tg(msg)
    print(msg)

if __name__ == "__main__":
    check()
