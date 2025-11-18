from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.models import db
from config.settings import settings

router = Router()

# Проверка прав администратора
def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS

# States для FSM
class CarStates(StatesGroup):
    waiting_for_car_name = State()
    waiting_for_car_plate = State()
    waiting_for_purchase_price = State()
    waiting_for_maintenance_car = State()
    waiting_for_maintenance_amount = State()
    waiting_for_maintenance_description = State()
    waiting_for_sale_price = State()

# === КОМАНДЫ АДМИН-ПАНЕЛИ ===

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Главное меню админ-панели"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ У вас нет доступа к админ-панели.")
        return
    
    admin_menu = """
    🛠️ <b>Админ-панель</b>

    <b>Управление автомобилями:</b>
    /add_car - Добавить автомобиль
    /cars - Список автомобилей
    /sell_car - Продать автомобиль
    /delete_car - Удалить автомобиль

    <b>Обслуживание:</b>
    /add_maintenance - Добавить расход на обслуживание
    /maintenance - История обслуживания

    <b>Статистика:</b>
    /finance - Финансовая статистика
    """
    
    await message.reply(admin_menu, parse_mode="HTML")

# === УПРАВЛЕНИЕ АВТОМОБИЛЯМИ ===

@router.message(Command("add_car"))
async def add_car_start(message: Message, state: FSMContext):
    """Начало добавления автомобиля"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ У вас нет доступа к этой команде.")
        return
    
    await message.reply("🚗 Введите название автомобиля:")
    await state.set_state(CarStates.waiting_for_car_name)

@router.message(CarStates.waiting_for_car_name)
async def add_car_name(message: Message, state: FSMContext):
    """Получение названия автомобиля"""
    await state.update_data(car_name=message.text)
    await message.reply("🔢 Введите номерной знак автомобиля:")
    await state.set_state(CarStates.waiting_for_car_plate)

@router.message(CarStates.waiting_for_car_plate)
async def add_car_plate(message: Message, state: FSMContext):
    """Получение номерного знака"""
    await state.update_data(car_plate=message.text.upper())
    await message.reply("💰 Введите цену покупки автомобиля ($):")
    await state.set_state(CarStates.waiting_for_purchase_price)

@router.message(CarStates.waiting_for_purchase_price)
async def add_car_price(message: Message, state: FSMContext):
    """Получение цены и сохранение автомобиля"""
    try:
        price = float(message.text.replace(',', '').replace(' ', ''))
        data = await state.get_data()
        
        if db.add_car(data['car_name'], data['car_plate'], price):
            await message.reply(
                f"✅ Автомобиль успешно добавлен!\n"
                f"🚗 {data['car_name']}\n"
                f"🔢 {data['car_plate']}\n"
                f"💰 ${price:,.2f}"
            )
        else:
            await message.reply("❌ Ошибка при добавлении автомобиля. Возможно, номерной знак уже существует.")
        
        await state.clear()
    except ValueError:
        await message.reply("❌ Неверный формат цены. Введите число:")

@router.message(Command("cars"))
async def list_cars(message: Message):
    """Список всех автомобилей"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ У вас нет доступа к этой команде.")
        return
    
    cars = db.get_all_cars()
    if not cars:
        await message.reply("📝 Список автомобилей пуст.")
        return
    
    response = "🚗 <b>Список автомобилей:</b>\n\n"
    for car in cars:
        status_icons = {
            'available': '✅',
            'rented': '🔵',
            'sold': '💰',
            'maintenance': '🛠️'
        }
        icon = status_icons.get(car['status'], '❓')
        
        response += (
            f"{icon} <b>{car['name']}</b>\n"
            f"🔢 Номер: {car['license_plate']}\n"
            f"📊 Статус: {car['status']}\n"
            f"💰 Покупка: ${car['purchase_price']:,.2f}\n"
        )
        
        if car['sale_price']:
            profit = car['sale_price'] - car['purchase_price']
            profit_icon = "📈" if profit > 0 else "📉"
            response += f"💰 Продажа: ${car['sale_price']:,.2f} ({profit_icon} ${profit:,.2f})\n"
        
        response += "\n"
    
    await message.reply(response, parse_mode="HTML")

@router.message(Command("sell_car"))
async def sell_car_start(message: Message, state: FSMContext):
    """Начало процесса продажи автомобиля"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ У вас нет доступа к этой команде.")
        return
    
    await message.reply("🔢 Введите номерной знак автомобиля для продажи:")
    # Здесь можно добавить состояние для получения номера и цены продажи

@router.message(Command("delete_car"))
async def delete_car_command(message: Message):
    """Удаление автомобиля"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ У вас нет доступа к этой команде.")
        return
    
    # Простой вариант - удаление по номеру из команды
    args = message.text.split()
    if len(args) < 2:
        await message.reply("❌ Используйте: /delete_car [номерной_знак]")
        return
    
    license_plate = args[1].upper()
    if db.delete_car(license_plate):
        await message.reply(f"✅ Автомобиль с номером {license_plate} удален.")
    else:
        await message.reply("❌ Ошибка при удалении автомобиля.")

# === ОБСЛУЖИВАНИЕ ===

@router.message(Command("add_maintenance"))
async def add_maintenance_start(message: Message, state: FSMContext):
    """Начало добавления расхода на обслуживание"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ У вас нет доступа к этой команде.")
        return
    
    await message.reply("🔢 Введите номерной знак автомобиля:")
    await state.set_state(CarStates.waiting_for_maintenance_car)

@router.message(CarStates.waiting_for_maintenance_car)
async def process_maintenance_car(message: Message, state: FSMContext):
    """Получение автомобиля для обслуживания"""
    license_plate = message.text.upper()
    car = db.get_car(license_plate)
    
    if not car:
        await message.reply("❌ Автомобиль с таким номерным знаком не найден.")
        await state.clear()
        return
    
    await state.update_data(car_id=car['id'], car_name=car['name'])
    await message.reply("💰 Введите сумму расхода на обслуживание ($):")
    await state.set_state(CarStates.waiting_for_maintenance_amount)

@router.message(CarStates.waiting_for_maintenance_amount)
async def process_maintenance_amount(message: Message, state: FSMContext):
    """Получение суммы обслуживания"""
    try:
        amount = float(message.text.replace(',', '').replace(' ', ''))
        await state.update_data(maintenance_amount=amount)
        await message.reply("📝 Введите описание расхода (например: 'Замена масла'):")
        await state.set_state(CarStates.waiting_for_maintenance_description)
    except ValueError:
        await message.reply("❌ Неверный формат суммы. Введите число:")

@router.message(CarStates.waiting_for_maintenance_description)
async def process_maintenance_description(message: Message, state: FSMContext):
    """Получение описания и сохранение обслуживания"""
    data = await state.get_data()
    
    if db.add_maintenance(data['car_id'], data['maintenance_amount'], message.text):
        await message.reply(
            f"✅ Расход на обслуживание добавлен!\n"
            f"🚗 {data['car_name']}\n"
            f"💰 ${data['maintenance_amount']:,.2f}\n"
            f"📝 {message.text}"
        )
    else:
        await message.reply("❌ Ошибка при добавлении расхода.")
    
    await state.clear()

@router.message(Command("maintenance"))
async def list_maintenance(message: Message):
    """История обслуживания"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ У вас нет доступа к этой команде.")
        return
    
    maintenance = db.get_all_maintenance()
    if not maintenance:
        await message.reply("📝 История обслуживания пуста.")
        return
    
    response = "🛠️ <b>История обслуживания:</b>\n\n"
    total_amount = 0
    
    for record in maintenance:
        total_amount += record['amount']
        response += (
            f"🚗 {record['car_name']} ({record['license_plate']})\n"
            f"💰 ${record['amount']:,.2f}\n"
            f"📝 {record['description']}\n"
            f"📅 {record['maintenance_date']}\n\n"
        )
    
    response += f"<b>Общая сумма расходов: ${total_amount:,.2f}</b>"
    await message.reply(response, parse_mode="HTML")

# === ФИНАНСОВАЯ СТАТИСТИКА ===

@router.message(Command("finance"))
async def finance_stats(message: Message):
    """Финансовая статистика"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ У вас нет доступа к этой команде.")
        return
    
    rentals = db.get_all_rentals()
    cars = db.get_all_cars()
    maintenance = db.get_all_maintenance()
    
    total_income = sum(rental['price'] for rental in rentals)
    total_car_cost = sum(car['purchase_price'] for car in cars)
    total_maintenance = sum(record['amount'] for record in maintenance)
    total_car_sales = sum(car['sale_price'] for car in cars if car['sale_price'])
    
    net_profit = total_income + total_car_sales - total_car_cost - total_maintenance
    
    response = (
        "💰 <b>Финансовая статистика</b>\n\n"
        f"📈 <b>Доход от аренд:</b> ${total_income:,.2f}\n"
        f"🚗 <b>Затраты на автомобили:</b> ${total_car_cost:,.2f}\n"
        f"🛠️ <b>Затраты на обслуживание:</b> ${total_maintenance:,.2f}\n"
        f"💰 <b>Доход от продаж:</b> ${total_car_sales:,.2f}\n"
        f"💵 <b>Чистая прибыль:</b> ${net_profit:,.2f}\n\n"
        f"📊 <b>Всего аренд:</b> {len(rentals)}\n"
        f"🚗 <b>Всего автомобилей:</b> {len(cars)}"
    )
    
    await message.reply(response, parse_mode="HTML")