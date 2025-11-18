from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.models import db
from config.settings import settings
from keyboards.admin_keyboards import *

router = Router()

# Проверка прав администратора
def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS

# States для FSM
class ExpenseStates(StatesGroup):
    waiting_for_advertisement_amount = State()
    waiting_for_advertisement_description = State()
    waiting_for_other_cost_amount = State()
    waiting_for_other_cost_description = State()

# === ОБРАБОТКА РАСХОДОВ НА РЕКЛАМУ ===

@router.callback_query(F.data == "expenses_advertisement")
async def advertisement_expenses_menu(callback: CallbackQuery):
    """Меню расходов на рекламу"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет доступа")
        return
    
    expenses = db.get_all_advertisement_costs()
    total = db.get_advertisement_costs_total()
    
    response = "📢 <b>Расходы на рекламу и объявления</b>\n\n"
    
    if expenses:
        for expense in expenses[:10]:  # Показываем последние 10
            response += (
                f"💰 ${expense['amount']:,.2f}\n"
                f"📝 {expense['description']}\n"
                f"📅 {expense['advertisement_date']}\n\n"
            )
    else:
        response += "📝 Нет записей о расходах на рекламу\n\n"
    
    response += f"<b>Общая сумма: ${total:,.2f}</b>"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="➕ Добавить расход", callback_data="add_advertisement_cost"),
        InlineKeyboardButton(text="🗑️ Очистить историю", callback_data="clear_advertisement_costs"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main")
    )
    keyboard.adjust(1)
    
    await callback.message.edit_text(
        response,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "add_advertisement_cost")
async def add_advertisement_cost_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления расхода на рекламу"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет доступа")
        return
    
    await callback.message.edit_text(
        "📢 <b>Добавление расхода на рекламу</b>\n\n"
        "💰 Введите сумму расхода ($):",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await state.set_state(ExpenseStates.waiting_for_advertisement_amount)

@router.message(ExpenseStates.waiting_for_advertisement_amount)
async def process_advertisement_amount(message: Message, state: FSMContext):
    """Получение суммы расхода на рекламу"""
    try:
        amount = float(message.text.replace(',', '').replace(' ', ''))
        await state.update_data(amount=amount)
        
        await message.answer(
            f"📢 <b>Добавление расхода на рекламу</b>\n\n"
            f"💰 Сумма: ${amount:,.2f}\n\n"
            f"📝 Введите описание расхода (например: 'Реклама в газете'):",
            reply_markup=get_back_button(),
            parse_mode="HTML"
        )
        await state.set_state(ExpenseStates.waiting_for_advertisement_description)
    except ValueError:
        await message.reply("❌ Неверный формат суммы. Введите число:")

@router.message(ExpenseStates.waiting_for_advertisement_description)
async def process_advertisement_description(message: Message, state: FSMContext):
    """Получение описания и сохранение расхода на рекламу"""
    data = await state.get_data()
    
    if db.add_advertisement_cost(data['amount'], message.text):
        await message.answer(
            f"✅ <b>Расход на рекламу добавлен!</b>\n\n"
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

# === ОБРАБОТКА ПРОЧИХ РАСХОДОВ ===

@router.callback_query(F.data == "expenses_other")
async def other_expenses_menu(callback: CallbackQuery):
    """Меню прочих расходов"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет доступа")
        return
    
    expenses = db.get_all_other_costs()
    total = db.get_other_costs_total()
    
    response = "📋 <b>Прочие расходы</b>\n\n"
    
    if expenses:
        for expense in expenses[:10]:  # Показываем последние 10
            response += (
                f"💰 ${expense['amount']:,.2f}\n"
                f"📝 {expense['description']}\n"
                f"📅 {expense['cost_date']}\n\n"
            )
    else:
        response += "📝 Нет записей о прочих расходах\n\n"
    
    response += f"<b>Общая сумма: ${total:,.2f}</b>"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="➕ Добавить расход", callback_data="add_other_cost"),
        InlineKeyboardButton(text="🗑️ Очистить историю", callback_data="clear_other_costs"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main")
    )
    keyboard.adjust(1)
    
    await callback.message.edit_text(
        response,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "add_other_cost")
async def add_other_cost_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления прочего расхода"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет доступа")
        return
    
    await callback.message.edit_text(
        "📋 <b>Добавление прочего расхода</b>\n\n"
        "💰 Введите сумму расхода ($):",
        reply_markup=get_back_button(),
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
            f"📝 Введите описание расхода (например: 'Аренда гаража'):",
            reply_markup=get_back_button(),
            parse_mode="HTML"
        )
        await state.set_state(ExpenseStates.waiting_for_other_cost_description)
    except ValueError:
        await message.reply("❌ Неверный формат суммы. Введите число:")

@router.message(ExpenseStates.waiting_for_other_cost_description)
async def process_other_cost_description(message: Message, state: FSMContext):
    """Получение описания и сохранение прочего расхода"""
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

# === ОБНОВЛЕННАЯ ФИНАНСОВАЯ СТАТИСТИКА ===

@router.callback_query(F.data == "admin_finance")
async def admin_finance_menu(callback: CallbackQuery):
    """Расширенная финансовая статистика"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет доступа")
        return
    
    financial_stats = db.get_financial_stats()
    expense_stats = db.get_expense_stats()
    
    response = (
        "💰 <b>Расширенная финансовая статистика</b>\n\n"
        f"📈 <b>Доход от аренд:</b> ${financial_stats['rental_income']:,.2f}\n"
        f"💰 <b>Доход от продаж:</b> ${financial_stats['sales_income']:,.2f}\n"
        f"💵 <b>Общий доход:</b> ${financial_stats['total_income']:,.2f}\n\n"
        
        f"🛠️ <b>Расходы на обслуживание:</b> ${expense_stats['expenses']['maintenance']:,.2f}\n"
        f"📢 <b>Расходы на рекламу:</b> ${expense_stats['expenses']['advertisement']:,.2f}\n"
        f"📋 <b>Прочие расходы:</b> ${expense_stats['expenses']['other_costs']:,.2f}\n"
        f"🚗 <b>Затраты на автомобили:</b> ${expense_stats['expenses']['car_costs']:,.2f}\n"
        f"💸 <b>Общие расходы:</b> ${expense_stats['expenses']['total']:,.2f}\n\n"
        
        f"📊 <b>Соотношение расход/доход:</b> {expense_stats['expense_income_ratio']:.1f}%\n"
        f"💎 <b>Чистая прибыль:</b> ${financial_stats['net_profit']:,.2f}\n"
        f"📈 <b>Рентабельность:</b> {financial_stats['profitability']:.1f}%\n\n"
        
        f"📊 <b>Всего аренд:</b> {financial_stats['total_rentals']}\n"
        f"🚗 <b>Всего автомобилей:</b> {financial_stats['total_cars']}"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="📢 Рекламные расходы", callback_data="expenses_advertisement"),
        InlineKeyboardButton(text="📋 Прочие расходы", callback_data="expenses_other"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main")
    )
    keyboard.adjust(1)
    
    await callback.message.edit_text(
        response,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )