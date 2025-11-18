from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from database.models import db
from utils.reporter import generate_html_report
from config.settings import settings

router = Router()

@router.message(Command("stats"))
async def handle_stats_command(message: Message):
    """Генерирует статистику по арендам"""
    if message.from_user.id not in settings.ADMIN_IDS:
        await message.reply("❌ У вас нет доступа к этой команде.")
        return
    
    try:
        # Получаем все аренды
        rentals = db.get_all_rentals()
        
        if not rentals:
            await message.reply("📊 Нет данных об арендах для генерации статистики.")
            return
        
        # Генерируем HTML отчет
        filename = await generate_html_report(rentals)
        
        # Отправляем файл
        document = FSInputFile(filename)
        await message.answer_document(
            document,
            caption="📊 Статистика аренды транспорта"
        )
        
    except Exception as e:
        await message.reply("❌ Ошибка при генерации статистики.")