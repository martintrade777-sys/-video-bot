import requests, json, os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
PEXELS_KEY = "s5U1lsRF7d5tOZbyqJ75hsydYUxiyd0eOqRjmMzRJaxqWI0oe3wTgAYM"

transcript = "Слушай, деньги не покупают любовь, это и так понятно. Но они покупают охренительный фильтр. Когда у тебя в кармане..."

resp = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Для цього транскрипту згенеруй 4 B-roll вставки. Відповідь ТІЛЬКИ JSON масив: [{\"keyword\": \"money cash\", \"time\": 1.5}]. Відео 8 сек. Ключові слова прості англійські 1-2 слова. Транскрипт: " + transcript}],
    max_tokens=200
)

raw = resp.choices[0].message.content
data = json.loads(raw[raw.find("["):raw.rfind("]")+1])
print("AI вставки:", json.dumps(data, ensure_ascii=False))

def get_video_url(keyword):
    r = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": keyword, "per_page": 3, "orientation": "portrait"}
    )
    for v in r.json().get("videos", []):
        for f in v["video_files"]:
            if f["quality"] == "hd":
                return f["link"]
    return None

inserts = []
for item in data:
    url = get_video_url(item["keyword"])
    if url:
        inserts.append({"keyword": item["keyword"], "time": item["time"], "url": url})
        print("OK: " + item["keyword"])
    else:
        print("НЕ ЗНАЙДЕНО: " + item["keyword"])

print("\nФінальні вставки:")
print(json.dumps(inserts, ensure_ascii=False, indent=2))
