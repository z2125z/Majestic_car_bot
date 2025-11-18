from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.models import db
from config.settings import settings
from keyboards.admin_keyboards import *
from utils.reporter import generate_html_report

router = Router()

# Проверка прав администратора
def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS

# States для FSM
class CarStates(StatesGroup):
    waiting_for_car_name = State()
    waiting_for_car_plate = State()
    waiting_for_purchase_price = State()
    waiting_for_sale_price = State()

class MaintenanceStates(StatesGroup):
    waiting_for_car_selection = State()
    waiting_for_maintenance_amount = State()
    waiting_for_maintenance_description = State()

class ExpenseStates(StatesGroup):
    waiting_for_advertisement_amount = State()
    waiting_for_advertisement_description = State()
    waiting_for_other_cost_amount = State()
    waiting_for_other_cost_description = State()

# === ОБРАБОТКА КОМАНД ===

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Главное меню админ-панели"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ У вас нет доступа к админ-панели.")
        return
    
    await message.answer(
        "🛠️ <b>Админ-панель</b>\n\n"
        "Выберите раздел для управления:",
        reply_markup=get_admin_main_menu(),
        parse_mode="HTML"
    )

# === ОБРАБОТКА CALLBACK-ЗАПРОСОВ ===

@router.callback_query(F.data == "admin_main")
async def admin_main_menu(callback: CallbackQuery):
    """Главное меню админ-панели"""
    await callback.message.edit_text(
        "🛠️ <b>Админ-панель</b>\n\n"
        "Выберите раздел для управления:",
        reply_markup=get_admin_main_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "admin_cars")
async def admin_cars_menu(callback: CallbackQuery):
    """Меню управления автомобилями"""
    await callback.message.edit_text(
        "🚗 <b>Управление автомобилями</b>\n\n"
        "Выберите действие:",
        reply_markup=get_cars_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "admin_reports")
async def admin_reports_menu(callback: CallbackQuery):
    """Меню отчетов"""
    await callback.message.edit_text(
        "📊 <b>Отчеты и статистика</b>\n\n"
        "Выберите тип отчета:",
        reply_markup=get_reports_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "admin_maintenance")
async def admin_maintenance_menu(callback: CallbackQuery):
    """Меню обслуживания"""
    await callback.message.edit_text(
        "🛠️ <b>Обслуживание автомобилей</b>\n\n"
        "Выберите действие:",
        reply_markup=get_maintenance_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "admin_expenses")
async def admin_expenses_menu(callback: CallbackQuery):
    """Меню управления расходами"""
    await callback.message.edit_text(
        "💸 <b>Управление расходами</b>\n\n"
        "Выберите тип расходов:",
        reply_markup=get_expenses_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "admin_finance")
async def admin_finance_menu(callback: CallbackQuery):
    """Финансовая статистика"""
    financial_stats = db.get_financial_stats()
    expense_stats = db.get_expense_stats()
    
    response = (
        "💰 <b>Финансовая статистика</b>\n\n"
        f"📈 <b>Доход от аренд:</b> ${financial_stats['rental_income']:,.2f}\n"
        f"💰 <b>Доход от продаж:</b> ${financial_stats['sales_income']:,.2f}\n"
        f"💵 <b>Общий доход:</b> ${financial_stats['total_income']:,.2f}\n\n"
        
        f"🛠️ <b>Расходы на обслуживание:</b> ${expense_stats['expenses']['maintenance']:,.2f}\n"
        f"📢 <b>Расходы на рекламу:</b> ${expense_stats['expenses']['advertisement']:,.2f}\n"
        f"📋 <b>Прочие расходы:</b> ${expense_stats['expenses']['other_costs']:,.2f}\n"
        f"🚗 <b>Затраты на автомобили:</b> ${expense_stats['expenses']['car_costs']:,.2f}\n"
        f"💸 <b>Общие расходы:</b> ${expense_stats['expenses']['total']:,.2f}\n\n"
        
        f"💎 <b>Чистая прибыль:</b> ${financial_stats['net_profit']:,.2f}\n"
        f"📈 <b>Рентабельность:</b> {financial_stats['profitability']:.1f}%\n\n"
        
        f"📊 <b>Всего аренд:</b> {financial_stats['total_rentals']}\n"
        f"🚗 <b>Всего автомобилей:</b> {financial_stats['total_cars']}"
    )
    
    await callback.message.edit_text(
        response,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )

# === УПРАВЛЕНИЕ АВТОМОБИЛЯМИ ===

@router.callback_query(F.data == "cars_add")
async def add_car_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления автомобиля"""
    await callback.message.edit_text(
        "🚗 <b>Добавление автомобиля</b>\n\n"
        "Введите название автомобиля:",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await state.set_state(CarStates.waiting_for_car_name)

@router.message(CarStates.waiting_for_car_name)
async def add_car_name(message: Message, state: FSMContext):
    """Получение названия автомобиля"""
    await state.update_data(car_name=message.text)
    await message.answer(
        "🔢 Введите номерной знак автомобиля:",
        reply_markup=get_back_button()
    )
    await state.set_state(CarStates.waiting_for_car_plate)

@router.message(CarStates.waiting_for_car_plate)
async def add_car_plate(message: Message, state: FSMContext):
    """Получение номерного знака"""
    await state.update_data(car_plate=message.text.upper())
    await message.answer(
        "💰 Введите цену покупки автомобиля ($):",
        reply_markup=get_back_button()
    )
    await state.set_state(CarStates.waiting_for_purchase_price)

@router.message(CarStates.waiting_for_purchase_price)
async def add_car_price(message: Message, state: FSMContext):
    """Получение цены и сохранение автомобиля"""
    try:
        price = float(message.text.replace(',', '').replace(' ', ''))
        data = await state.get_data()
        
        if db.add_car(data['car_name'], data['car_plate'], price):
            await message.answer(
                f"✅ <b>Автомобиль успешно добавлен!</b>\n\n"
                f"🚗 {data['car_name']}\n"
                f"🔢 {data['car_plate']}\n"
                f"💰 ${price:,.2f}",
                reply_markup=get_admin_main_menu(),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ Ошибка при добавлении автомобиля. Возможно, номерной знак уже существует.",
                reply_markup=get_admin_main_menu()
            )
        
        await state.clear()
    except ValueError:
        await message.reply("❌ Неверный формат цены. Введите число:")

@router.callback_query(F.data == "cars_list")
async def cars_list_handler(callback: CallbackQuery):
    """Список автомобилей"""
    cars = db.get_all_cars()
    if not cars:
        await callback.message.edit_text(
            "📝 Список автомобилей пуст.",
            reply_markup=get_back_to_cars_button()
        )
        return
    
    await callback.message.edit_text(
        "🚗 <b>Выберите автомобиль:</b>",
        reply_markup=get_cars_list_keyboard(cars),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("cars_page_"))
async def cars_list_pagination(callback: CallbackQuery):
    """Пагинация списка автомобилей"""
    page = int(callback.data.split("_")[2])
    cars = db.get_all_cars()
    
    await callback.message.edit_text(
        "🚗 <b>Выберите автомобиль:</b>",
        reply_markup=get_cars_list_keyboard(cars, page),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("car_detail_"))
async def car_detail_handler(callback: CallbackQuery):
    """Детали автомобиля"""
    car_id = int(callback.data.split("_")[2])
    car = db.get_car_by_id(car_id)
    
    if not car:
        await callback.answer("❌ Автомобиль не найден")
        return
    
    status_icons = {
        'available': '✅',
        'rented': '🔵',
        'sold': '💰',
        'maintenance': '🛠️'
    }
    icon = status_icons.get(car['status'], '❓')
    
    response = (
        f"{icon} <b>Детали автомобиля</b>\n\n"
        f"🚗 <b>Название:</b> {car['name']}\n"
        f"🔢 <b>Номерной знак:</b> {car['license_plate']}\n"
        f"📊 <b>Статус:</b> {car['status']}\n"
        f"💰 <b>Цена покупки:</b> ${car['purchase_price']:,.2f}\n"
        f"📈 <b>Доход от аренд:</b> ${car.get('total_income', 0):,.2f}\n"
        f"🔢 <b>Количество аренд:</b> {car.get('total_rentals', 0)}"
    )
    
    if car['sale_price']:
        profit = car['sale_price'] - car['purchase_price']
        profit_icon = "📈" if profit > 0 else "📉"
        response += f"\n💰 <b>Цена продажи:</b> ${car['sale_price']:,.2f}"
        response += f"\n{profit_icon} <b>Прибыль:</b> ${profit:,.2f}"
    
    await callback.message.edit_text(
        response,
        reply_markup=get_car_detail_keyboard(car_id),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("car_delete_"))
async def car_delete_handler(callback: CallbackQuery):
    """Подтверждение удаления автомобиля"""
    car_id = int(callback.data.split("_")[2])
    car = db.get_car_by_id(car_id)
    
    if not car:
        await callback.answer("❌ Автомобиль не найден")
        return
    
    await callback.message.edit_text(
        f"❌ <b>Подтверждение удаления</b>\n\n"
        f"Вы уверены, что хотите удалить автомобиль?\n"
        f"🚗 {car['name']} ({car['license_plate']})",
        reply_markup=get_confirmation_keyboard("delete_car", car_id),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("confirm_delete_car_"))
async def confirm_car_delete(callback: CallbackQuery):
    """Подтвержденное удаление автомобиля"""
    car_id = int(callback.data.split("_")[3])
    car = db.get_car_by_id(car_id)
    
    if car and db.delete_car(car['license_plate']):
        await callback.message.edit_text(
            f"✅ Автомобиль {car['name']} ({car['license_plate']}) успешно удален.",
            reply_markup=get_back_to_cars_button()
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка при удалении автомобиля.",
            reply_markup=get_back_to_cars_button()
        )

@router.callback_query(F.data.startswith("cancel_delete_car_"))
async def cancel_car_delete(callback: CallbackQuery):
    """Отмена удаления автомобиля"""
    car_id = int(callback.data.split("_")[3])
    await car_detail_handler(callback)

@router.callback_query(F.data.startswith("car_sell_"))
async def car_sell_handler(callback: CallbackQuery, state: FSMContext):
    """Начало процесса продажи автомобиля"""
    car_id = int(callback.data.split("_")[2])
    car = db.get_car_by_id(car_id)
    
    if not car:
        await callback.answer("❌ Автомобиль не найден")
        return
    
    await state.update_data(car_id=car_id, car_plate=car['license_plate'])
    
    await callback.message.edit_text(
        f"💰 <b>Продажа автомобиля</b>\n\n"
        f"🚗 {car['name']} ({car['license_plate']})\n\n"
        f"💰 Введите цену продажи ($):",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await state.set_state(CarStates.waiting_for_sale_price)

@router.message(CarStates.waiting_for_sale_price)
async def process_sale_price(message: Message, state: FSMContext):
    """Обработка цены продажи"""
    try:
        sale_price = float(message.text.replace(',', '').replace(' ', ''))
        data = await state.get_data()
        
        if db.sell_car(data['car_plate'], sale_price):
            await message.answer(
                f"✅ <b>Автомобиль успешно продан!</b>\n\n"
                f"💰 Цена продажи: ${sale_price:,.2f}",
                reply_markup=get_admin_main_menu(),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ Ошибка при продаже автомобиля.",
                reply_markup=get_admin_main_menu()
            )
        
        await state.clear()
    except ValueError:
        await message.reply("❌ Неверный формат цены. Введите число:")

# === ОБСЛУЖИВАНИЕ ===

@router.callback_query(F.data == "maintenance_add")
async def maintenance_add_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления обслуживания"""
    cars = db.get_all_cars()
    
    if not cars:
        await callback.message.edit_text(
            "❌ Нет автомобилей для обслуживания.",
            reply_markup=get_back_button()
        )
        return
    
    await callback.message.edit_text(
        "🛠️ <b>Добавление расхода на обслуживание</b>\n\n"
        "Выберите автомобиль:",
        reply_markup=get_cars_for_maintenance_keyboard(cars),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("maintenance_for_car_"))
async def maintenance_for_car_handler(callback: CallbackQuery, state: FSMContext):
    """Выбор автомобиля для обслуживания"""
    car_id = int(callback.data.split("_")[3])
    car = db.get_car_by_id(car_id)
    
    if not car:
        await callback.answer("❌ Автомобиль не найден")
        return
    
    await state.update_data(car_id=car_id, car_name=car['name'])
    
    await callback.message.edit_text(
        f"🛠️ <b>Добавление расхода</b>\n\n"
        f"🚗 Автомобиль: {car['name']} ({car['license_plate']})\n\n"
        f"💰 Введите сумму расхода на обслуживание ($):",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await state.set_state(MaintenanceStates.waiting_for_maintenance_amount)

@router.message(MaintenanceStates.waiting_for_maintenance_amount)
async def process_maintenance_amount(message: Message, state: FSMContext):
    """Получение суммы обслуживания"""
    try:
        amount = float(message.text.replace(',', '').replace(' ', ''))
        await state.update_data(maintenance_amount=amount)
        
        data = await state.get_data()
        
        await message.answer(
            f"🛠️ <b>Добавление расхода</b>\n\n"
            f"🚗 Автомобиль: {data['car_name']}\n"
            f"💰 Сумма: ${amount:,.2f}\n\n"
            f"📝 Введите описание расхода:",
            reply_markup=get_back_button(),
            parse_mode="HTML"
        )
        await state.set_state(MaintenanceStates.waiting_for_maintenance_description)
    except ValueError:
        await message.reply("❌ Неверный формат суммы. Введите число:")

@router.message(MaintenanceStates.waiting_for_maintenance_description)
async def process_maintenance_description(message: Message, state: FSMContext):
    """Получение описания и сохранение обслуживания"""
    data = await state.get_data()
    
    if db.add_maintenance(data['car_id'], data['maintenance_amount'], message.text):
        await message.answer(
            f"✅ <b>Расход на обслуживание добавлен!</b>\n\n"
            f"🚗 {data['car_name']}\n"
            f"💰 ${data['maintenance_amount']:,.2f}\n"
            f"📝 {message.text}",
            reply_markup=get_admin_main_menu(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ Ошибка при добавлении расхода.",
            reply_markup=get_admin_main_menu()
        )
    
    await state.clear()

@router.callback_query(F.data == "maintenance_list")
async def maintenance_list_handler(callback: CallbackQuery):
    """Список обслуживания"""
    maintenance = db.get_all_maintenance()
    
    if not maintenance:
        await callback.message.edit_text(
            "📝 История обслуживания пуста.",
            reply_markup=get_back_button()
        )
        return
    
    total = db.get_maintenance_total()
    
    response = f"🛠️ <b>История обслуживания</b>\n\n"
    response += f"<b>Общая сумма: ${total:,.2f}</b>\n\n"
    
    await callback.message.edit_text(
        response,
        reply_markup=get_maintenance_list_keyboard(maintenance),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("maintenance_page_"))
async def maintenance_list_pagination(callback: CallbackQuery):
    """Пагинация списка обслуживания"""
    page = int(callback.data.split("_")[2])
    maintenance = db.get_all_maintenance()
    total = db.get_maintenance_total()
    
    response = f"🛠️ <b>История обслуживания</b>\n\n"
    response += f"<b>Общая сумма: ${total:,.2f}</b>\n\n"
    
    await callback.message.edit_text(
        response,
        reply_markup=get_maintenance_list_keyboard(maintenance, page),
        parse_mode="HTML"
    )

# === РАСХОДЫ ===

@router.callback_query(F.data == "expenses_advertisement")
async def expenses_advertisement_menu(callback: CallbackQuery):
    """Меню рекламных расходов"""
    await callback.message.edit_text(
        "📢 <b>Рекламные расходы</b>\n\n"
        "Управление расходами на рекламу и объявления:",
        reply_markup=get_advertisement_expenses_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "expenses_other")
async def expenses_other_menu(callback: CallbackQuery):
    """Меню прочих расходов"""
    await callback.message.edit_text(
        "📋 <b>Прочие расходы</b>\n\n"
        "Управление прочими расходами:",
        reply_markup=get_other_expenses_menu(),
        parse_mode="HTML"
    )

# Рекламные расходы
@router.callback_query(F.data == "add_advertisement_cost")
async def add_advertisement_cost_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления рекламного расхода"""
    await callback.message.edit_text(
        "📢 <b>Добавление рекламного расхода</b>\n\n"
        "💰 Введите сумму расхода ($):",
        reply_markup=get_back_to_expenses_button(),
        parse_mode="HTML"
    )
    await state.set_state(ExpenseStates.waiting_for_advertisement_amount)

@router.message(ExpenseStates.waiting_for_advertisement_amount)
async def process_advertisement_amount(message: Message, state: FSMContext):
    """Получение суммы рекламного расхода"""
    try:
        amount = float(message.text.replace(',', '').replace(' ', ''))
        await state.update_data(amount=amount)
        
        await message.answer(
            f"📢 <b>Добавление рекламного расхода</b>\n\n"
            f"💰 Сумма: ${amount:,.2f}\n\n"
            f"📝 Введите описание расхода:",
            reply_markup=get_back_to_expenses_button(),
            parse_mode="HTML"
        )
        await state.set_state(ExpenseStates.waiting_for_advertisement_description)
    except ValueError:
        await message.reply("❌ Неверный формат суммы. Введите число:")

@router.message(ExpenseStates.waiting_for_advertisement_description)
async def process_advertisement_description(message: Message, state: FSMContext):
    """Сохранение рекламного расхода"""
    data = await state.get_data()
    
    if db.add_advertisement_cost(data['amount'], message.text):
        await message.answer(
            f"✅ <b>Рекламный расход добавлен!</b>\n\n"
            f"💰 ${data['amount']:,.2f}\n"
            f"📝 {message.text}",
            reply_markup=get_admin_main_menu(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ Ошибка при добавлении расхода.",
            reply_markup=get_admin_main_menu()
        )
    
    await state.clear()

@router.callback_query(F.data == "list_advertisement_costs")
async def list_advertisement_costs_handler(callback: CallbackQuery):
    """Список рекламных расходов"""
    costs = db.get_all_advertisement_costs()
    
    if not costs:
        await callback.message.edit_text(
            "📝 Нет записей о рекламных расходах.",
            reply_markup=get_back_to_expenses_button()
        )
        return
    
    total = db.get_advertisement_costs_total()
    
    response = f"📢 <b>Рекламные расходы</b>\n\n"
    response += f"<b>Общая сумма: ${total:,.2f}</b>\n\n"
    
    await callback.message.edit_text(
        response,
        reply_markup=get_advertisement_costs_keyboard(costs),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("advertisement_page_"))
async def advertisement_costs_pagination(callback: CallbackQuery):
    """Пагинация списка рекламных расходов"""
    page = int(callback.data.split("_")[2])
    costs = db.get_all_advertisement_costs()
    total = db.get_advertisement_costs_total()
    
    response = f"📢 <b>Рекламные расходы</b>\n\n"
    response += f"<b>Общая сумма: ${total:,.2f}</b>\n\n"
    
    await callback.message.edit_text(
        response,
        reply_markup=get_advertisement_costs_keyboard(costs, page),
        parse_mode="HTML"
    )

# Прочие расходы
@router.callback_query(F.data == "add_other_cost")
async def add_other_cost_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления прочего расхода"""
    await callback.message.edit_text(
        "📋 <b>Добавление прочего расхода</b>\n\n"
        "💰 Введите сумму расхода ($):",
        reply_markup=get_back_to_expenses_button(),
        parse_mode="HTML"
    )
    await state.set_state(ExpenseStates.waiting_for_other_cost_amount)

@router.message(ExpenseStates.waiting_for_other_cost_amount)
async def process_other_cost_amount(message: Message, state: FSMContext):
    """Получение суммы прочего расхода"""
    try:
        amount = float(message.text.replace(',', '').replace(' ', ''))
        await state.update_data(amount=amount)
        
        await message.answer(
            f"📋 <b>Добавление прочего расхода</b>\n\n"
            f"💰 Сумма: ${amount:,.2f}\n\n"
            f"📝 Введите описание расхода:",
            reply_markup=get_back_to_expenses_button(),
            parse_mode="HTML"
        )
        await state.set_state(ExpenseStates.waiting_for_other_cost_description)
    except ValueError:
        await message.reply("❌ Неверный формат суммы. Введите число:")

@router.message(ExpenseStates.waiting_for_other_cost_description)
async def process_other_cost_description(message: Message, state: FSMContext):
    """Сохранение прочего расхода"""
    data = await state.get_data()
    
    if db.add_other_cost(data['amount'], message.text):
        await message.answer(
            f"✅ <b>Прочий расход добавлен!</b>\n\n"
            f"💰 ${data['amount']:,.2f}\n"
            f"📝 {message.text}",
            reply_markup=get_admin_main_menu(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ Ошибка при добавлении расхода.",
            reply_markup=get_admin_main_menu()
        )
    
    await state.clear()

@router.callback_query(F.data == "list_other_costs")
async def list_other_costs_handler(callback: CallbackQuery):
    """Список прочих расходов"""
    costs = db.get_all_other_costs()
    
    if not costs:
        await callback.message.edit_text(
            "📝 Нет записей о прочих расходах.",
            reply_markup=get_back_to_expenses_button()
        )
        return
    
    total = db.get_other_costs_total()
    
    response = f"📋 <b>Прочие расходы</b>\n\n"
    response += f"<b>Общая сумма: ${total:,.2f}</b>\n\n"
    
    await callback.message.edit_text(
        response,
        reply_markup=get_other_costs_keyboard(costs),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("other_costs_page_"))
async def other_costs_pagination(callback: CallbackQuery):
    """Пагинация списка прочих расходов"""
    page = int(callback.data.split("_")[2])
    costs = db.get_all_other_costs()
    total = db.get_other_costs_total()
    
    response = f"📋 <b>Прочие расходы</b>\n\n"
    response += f"<b>Общая сумма: ${total:,.2f}</b>\n\n"
    
    await callback.message.edit_text(
        response,
        reply_markup=get_other_costs_keyboard(costs, page),
        parse_mode="HTML"
    )

# === ОТЧЕТЫ ===

@router.callback_query(F.data == "reports_html")
async def generate_html_report_handler(callback: CallbackQuery):
    """Генерация полного HTML отчета"""
    try:
        # Генерируем полный HTML отчет
        filename = await generate_html_report()
        
        # Отправляем файл
        from aiogram.types import FSInputFile
        document = FSInputFile(filename)
        
        await callback.message.answer_document(
            document,
            caption="📊 Полный отчет по аренде транспорта\n\n"
                   "✅ Включена вся статистика:\n"
                   "• 💰 Доходы и расходы\n"
                   "• 🚗 Статусы автомобилей\n" 
                   "• 🌐 Статистика по серверам\n"
                   "• 🛠️ История обслуживания\n"
                   "• 💸 Детализация расходов"
        )
        
        await callback.answer("✅ Полный HTML отчет сгенерирован")
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при генерации отчета: {str(e)}",
            reply_markup=get_back_button()
        )

# === ОБРАБОТКА ОТМЕНЫ ===

@router.callback_query(F.data.startswith("cancel_"))
async def cancel_operation(callback: CallbackQuery):
    """Отмена операции"""
    await admin_main_menu(callback)

# === ОБРАБОТКА НЕИЗВЕСТНЫХ CALLBACK-ЗАПРОСОВ ===

@router.callback_query()
async def unknown_callback(callback: CallbackQuery):
    """Обработка неизвестных callback-запросов"""
    await callback.answer("❌ Эта функция еще не реализована")