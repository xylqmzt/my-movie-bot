import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Получаем токен бота из настроек Render
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Переменная TELEGRAM_TOKEN не задана в настройках Render!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "🎬 **Привет! Я твой кинопоиск (на базе Kodik).**\n\n"
        "Напиши мне название фильма, сериала или аниме, и я найду его!",
        parse_mode="Markdown"
    )

@dp.message(F.text)
async def search_movie(message: types.Message):
    query = message.text
    waiting_msg = await message.answer("🔍 Ищу в базе Kodik...")
    
    # Используем публичное зеркало API Kodik, которое работает БЕЗ токена
    url = f"https://timeenjoy.club/api/kodik?title={query}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    movies = await response.json()
                    
                    if not movies or len(movies) == 0:
                        await waiting_msg.edit_text("😢 Ничего не нашлось. Проверь, нет ли ошибок в названии.")
                        return
                    
                    builder = InlineKeyboardBuilder()
                    text_reply = "🎬 **Вот что я нашёл в Kodik:**\n\n"
                    
                    # Показываем первые 5 результатов
                    for i, movie in enumerate(movies[:5]):
                        title = movie.get("title", "Без названия")
                        year = movie.get("year", "Год неизвестен")
                        link = movie.get("link", "")
                        
                        if not link:
                            continue
                            
                        # Если ссылка относительная, делаем её полной
                        if link.startswith("//"):
                            link = "https:" + link
                            
                        text_reply += f"{i+1}. **{title}** ({year})\n"
                        builder.button(text=f"Смотреть вариант {i+1} 🍿", url=link)
                    
                    builder.adjust(1)
                    await waiting_msg.delete()
                    await message.answer(text_reply, reply_markup=builder.as_markup(), parse_mode="Markdown")
                else:
                    await waiting_msg.edit_text("⚠️ Ошибка поиска. Попробуй другое название или зайди позже.")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await waiting_msg.edit_text("💥 Произошла ошибка при поиске.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
