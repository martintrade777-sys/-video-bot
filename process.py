import sys
import os
import shutil
from video_processor import process_video

BASE = os.path.expanduser(
    "~/Library/CloudStorage/GoogleDrive-martintrade777@gmail.com/Мій диск/VideoBot"
)

RAW_DIR = os.path.join(BASE, "raw")

DESTINATIONS = [
    os.path.join(BASE, "ready/Instagram/Акк1"),
    os.path.join(BASE, "ready/Instagram/Акк2"),
    os.path.join(BASE, "ready/TikTok/Акк1"),
    os.path.join(BASE, "ready/TikTok/Акк2"),
    os.path.join(BASE, "ready/YouTube/Акк1"),
    os.path.join(BASE, "ready/YouTube/Акк2"),
]

def main():
    videos = sorted([
        os.path.join(RAW_DIR, f)
        for f in os.listdir(RAW_DIR)
        if f.lower().endswith((".mp4", ".mov"))
        and not f.startswith(".")
    ])

    if not videos:
        print("❌ Немає відео в папці raw/")
        print(f"   Клади відео сюди: {RAW_DIR}")
        return

    print(f"📂 Знайдено {len(videos)} відео → буде {len(videos)*6} результатів\n")

    tmp_dir = os.path.join(BASE, "_tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    for i, video in enumerate(videos):
        name = os.path.splitext(os.path.basename(video))[0]
        print(f"{'='*50}")
        print(f"🎬 Відео {i+1}/{len(videos)}: {name}")
        print(f"{'='*50}")

        process_video(video, tmp_dir, name)

        for v_idx, dest in enumerate(DESTINATIONS):
            src = os.path.join(tmp_dir, f"{name}_v{v_idx+1}.mp4")
            if os.path.exists(src):
                dst = os.path.join(dest, f"{name}_v{v_idx+1}.mp4")
                shutil.move(src, dst)
                print(f"   ✅ → {dest.split('VideoBot/')[-1]}")
            else:
                print(f"   ❌ версія {v_idx+1} не знайдена")

        print()

    shutil.rmtree(tmp_dir, ignore_errors=True)

    total = sum(
        len([f for f in os.listdir(d) if f.endswith(".mp4")])
        for d in DESTINATIONS
    )
    print(f"🎉 Готово! {total} відео розкладено по папках")
    print(f"📁 Дивись в Google Drive → VideoBot → ready/")

if __name__ == "__main__":
    main()
