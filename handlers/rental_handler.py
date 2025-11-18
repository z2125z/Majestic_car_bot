from aiogram import Router, F
from aiogram.types import Message
from database.models import db
from utils.parser import parse_rental_message

router = Router()

@router.message(F.text.contains("Транспорт сдан в аренду"))
async def handle_rental_message(message: Message):
    """Обрабатывает сообщения о аренде транспорта"""
    parsed_data = parse_rental_message(message.text)
    
    if not parsed_data:
        await message.reply("❌ Не удалось распознать данные аренды. Проверьте формат сообщения.")
        return
    
    # Сохраняем в базу данных
    if db.add_rental(parsed_data):
        await message.reply(
            f"✅ Аренда успешно сохранена!\n"
            f"🚗 {parsed_data['transport']} ({parsed_data['license_plate']})\n"
            f"💰 ${parsed_data['price']} • ⏰ {parsed_data['duration']}"
        )
    else:
        await message.reply("❌ Ошибка при сохранении данных.")