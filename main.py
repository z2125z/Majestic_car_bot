import asyncio
import logging
from aiogram import Bot, Dispatcher
from config.settings import settings
from handlers.rental_handler import router as rental_router
from handlers.stats_handler import router as stats_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(rental_router)
    dp.include_router(stats_router)
    
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())