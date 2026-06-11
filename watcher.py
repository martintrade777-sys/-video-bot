import time, os, subprocess

RAW_DIR = os.path.expanduser(
    "~/Library/CloudStorage/GoogleDrive-martintrade777@gmail.com/Мій диск/VideoBot/raw"
)

def send_tg(text):
    import urllib.request, urllib.parse
    url = "https://api.telegram.org/bot8857862098:AAERoVN9gEq6abPj5qAOGJM_lU6iu7rXyK4/sendMessage"
    data = urllib.parse.urlencode({"chat_id": "5488407395", "text": text}).encode()
    try:
        urllib.request.urlopen(url, data)
    except:
        pass

def get_videos():
    return set(
        f for f in os.listdir(RAW_DIR)
        if f.lower().endswith((".mp4", ".mov")) and not f.startswith(".")
    )

print("Слідкую за raw/")
send_tg("🤖 Бот запущений! Кидай відео в Google Drive → VideoBot → raw/")

seen = get_videos()
print(f"Ігнорую {len(seen)} існуючих відео")
processing = False

while True:
    time.sleep(15)
    if processing:
        continue
    current = get_videos()
    new = current - seen
    if new:
        # Чекаємо 30 секунд щоб файл повністю завантажився
        print(f"Нові відео: {new}, чекаю 30 сек...")
        time.sleep(30)
        # Перевіряємо ще раз
        current = get_videos()
        new = current - seen
        if new:
            processing = True
            print(f"Обробляю: {new}")
            send_tg(f"📥 {len(new)} нових відео! Починаю обробку...")
            try:
                subprocess.run(
                    ["/Library/Frameworks/Python.framework/Versions/3.13/bin/python3", "process.py"],
                    cwd=os.path.dirname(__file__)
                )
                send_tg("✅ Готово! Відео в Google Drive → VideoBot → ready/")
            except Exception as e:
                send_tg("❌ Помилка: " + str(e))
            finally:
                processing = False
                seen = get_videos()
    else:
        print(".", end="", flush=True)
