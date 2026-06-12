import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Получаем токен из настроек Render
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Переменная TELEGRAM_TOKEN не задана в настройках Render!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Главное меню при команде /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "🎬 **Привет! Я твой личный кинопоиск.**\n\n"
        "Просто напиши мне название фильма, мультфильма или сериала, "
        "и я найду ссылку на просмотр!",
        parse_mode="Markdown"
    )

# Обработка текстовых сообщений (поиск фильма по названию)
@dp.message(F.text)
async def search_movie(message: types.Message):
    query = message.text
    waiting_msg = await message.answer("🔍 Ищу... Подожди секунду...")
    
    # URL API Кинобокса для поиска по тексту
    url = f"https://kinobox.tv/api/films/search?query={query}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    movies = await response.json()
                    
                    # Если ничего не нашли
                    if not movies or len(movies) == 0:
                        await waiting_msg.edit_text("😢 Ничего не нашлось по такому названию. Попробуй проверить ошибки в тексте.")
                        return
                    
                    # Берем первые 5 результатов, чтобы не спамить
                    builder = InlineKeyboardBuilder()
                    text_reply = "🎬 **Вот что я нашёл. Выбери нужный вариант:**\n\n"
                    
                    for i, movie in enumerate(movies[:5]):
                        title = movie.get("title", "Без названия")
                        year = movie.get("year", "Год неизвестен")
                        rating = movie.get("rating", "-")
                        kp_id = movie.get("kinopoiskId")
                        
                        if not kp_id:
                            continue
                            
                        # Добавляем фильм в текст со своим номером
                        text_reply += f"{i+1}. **{title}** ({year}) — Рейтинг: {rating}\n"
                        
                        # Делаем кнопку, которая ведет на бесплатный плеер Kinobox
                        watch_url = f"https://kinobox.tv/player?kp={kp_id}"
                        builder.button(text=f"Смотреть вариант {i+1} 🍿", url=watch_url)
                    
                    # Выстраиваем кнопки в один столбик
                    builder.adjust(1)
                    
                    await waiting_msg.delete() # Удаляем надпись "Ищу..."
                    await message.answer(text_reply, reply_markup=builder.as_markup(), parse_mode="Markdown")
                else:
                    await waiting_msg.edit_text("⚠️ Ошибка сервера поиска. Попробуй чуть позже.")
    except Exception as e:
        logging.error(f"Ошибка поиска: {e}")
        await waiting_msg.edit_text("💥 Произошла ошибка при поиске. Попробуй ещё раз.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
                        
