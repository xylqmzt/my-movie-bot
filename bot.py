import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
import aiohttp

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
KODIK_TOKEN = os.getenv("KODIK_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(F.text == "/start")
async def start_cmd(message: Message):
    await message.answer("🎬 **Привет!**\n\nНапиши мне название фильма, мультфильма или сериала, и я найду ссылку на просмотр!", parse_mode="Markdown")

@dp.message()
async def search_movie(message: Message):
    query = message.text
    status_msg = await message.answer(f"🔍 Ищу: *{query}*...", parse_mode="Markdown")

    url = f"https://kodikapi.com/search?token={KODIK_TOKEN}&title={query}&limit=5"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])

                    if not results:
                        await status_msg.edit_text("❌ Ничего не найдено. Попробуй другое название.")
                        return

                    response_text = "🍿 **Вот что я нашёл:**\n\n"
                    for movie in results:
                        title = movie.get("title", "Без названия")
                        year = movie.get("year", "Год неизвестен")
                        link = movie.get("link")
                        type_media = movie.get("type", "видео").replace("-", " ").capitalize()

                        response_text += f"🎬 *{title}* ({year}) — {type_media}\n🔗 [Смотреть фильм]({link})\n\n"

                    await status_msg.edit_text(response_text, parse_mode="Markdown", disable_web_page_preview=True)
                else:
                    await status_msg.edit_text("⚠️ Ошибка связи с базой данных.")
        except Exception as e:
            await status_msg.edit_text("🔥 Произошла ошибка при поиске.")
            print(f"Ошибка: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
                      
