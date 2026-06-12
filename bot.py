import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Переменная TELEGRAM_TOKEN не задана в настройках Render!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "🎬 **Привет! Я твой кинопоиск.**\n\n"
        "Напиши мне название фильма, сериала или аниме, и я найду ссылку на просмотр!",
        parse_mode="Markdown"
    )

@dp.message(F.text)
async def search_movie(message: types.Message):
    query = message.text
    waiting_msg = await message.answer("🔍 Ищу... Подожди секунду...")
    
    # Используем самое свежее и стабильное зеркало Kinobox
    url = f"https://kinobox.net/api/films/search?query={query}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    movies = await response.json()
                    
                    if not movies or len(movies) == 0:
                        await waiting_msg.edit_text("😢 Ничего не нашлось. Проверь, нет ли ошибок в названии.")
                        return
                    
                    builder = InlineKeyboardBuilder()
                    text_reply = "🎬 **Вот что я нашёл для тебя:**\n\n"
                    
                    for i, movie in enumerate(movies[:5]):
                        title = movie.get("title", "Без названия")
                        year = movie.get("year", "Год неизвестен")
                        rating = movie.get("rating", "-")
                        kp_id = movie.get("kinopoiskId")
                        
                        if not kp_id:
                            continue
                            
                        text_reply += f"{i+1}. **{title}** ({year}) — Рейтинг: {rating}\n"
                        # Ссылка сразу ведет на плеер этого зеркала
                        watch_url = f"https://kinobox.net/player?kp={kp_id}"
                        builder.button(text=f"Смотреть вариант {i+1} 🍿", url=watch_url)
                    
                    builder.adjust(1)
                    await waiting_msg.delete()
                    await message.answer(text_reply, reply_markup=builder.as_markup(), parse_mode="Markdown")
                else:
                    await waiting_msg.edit_text("⚠️ Ошибка поиска. Попробуй другое название.")
    except Exception as e:
        logging.error(f"Ошибка поиска: {e}")
        await waiting_msg.edit_text("💥 Произошла ошибка при поиске. Попробуй ещё раз.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
        
