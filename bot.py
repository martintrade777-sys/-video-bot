import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from video_processor import process_video

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8857862098:AAERoVN9gEq6abPj5qAOGJM_lU6iu7rXyK4"
OUTPUT_DIR = "output_videos"
DOWNLOAD_DIR = "downloads"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привіт! Надішли мені відео (до 100МБ) і я зроблю 6 унікальних варіантів!\n\n"
        "⏳ Обробка займає ~1-3 хвилини залежно від розміру."
    )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    video = message.video or message.document

    if not video:
        await message.reply_text("❌ Надішли відео файл!")
        return

    if video.file_size > 100 * 1024 * 1024:
        await message.reply_text("❌ Файл більше 100МБ! Скоротіть відео.")
        return

    status_msg = await message.reply_text("⬇️ Завантажую відео...")

    # Download video
    file = await context.bot.get_file(video.file_id)
    input_path = os.path.join(DOWNLOAD_DIR, f"{video.file_id}.mp4")
    await file.download_to_drive(input_path)

    await status_msg.edit_text("⚙️ Обробляю відео... Це займе 1-3 хвилини.")

    try:
        output_paths = await asyncio.to_thread(process_video, input_path, OUTPUT_DIR, video.file_id)

        await status_msg.edit_text(f"✅ Готово! Відправляю {len(output_paths)} варіантів...")

        for i, path in enumerate(output_paths, 1):
            with open(path, "rb") as f:
                await message.reply_video(
                    video=f,
                    caption=f"📹 Варіант {i}/6",
                    supports_streaming=True
                )
            await asyncio.sleep(1)

        await message.reply_text("🎉 Всі 6 варіантів готові! Кожне відео унікальне.")

    except Exception as e:
        logger.error(f"Error processing video: {e}")
        await status_msg.edit_text(f"❌ Помилка обробки: {str(e)}")

    finally:
        # Cleanup input
        if os.path.exists(input_path):
            os.remove(input_path)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))

    print("🤖 Бот запущено!")
    app.run_polling()


if __name__ == "__main__":
    main()

