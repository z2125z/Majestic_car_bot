from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Главное меню админ-панели
def get_admin_main_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🚗 Управление автомобилями", callback_data="admin_cars"),
        InlineKeyboardButton(text="💰 Финансовая статистика", callback_data="admin_finance"),
        InlineKeyboardButton(text="📊 Отчеты", callback_data="admin_reports"),
        InlineKeyboardButton(text="🛠️ Обслуживание", callback_data="admin_maintenance"),
        InlineKeyboardButton(text="💸 Управление расходами", callback_data="admin_expenses")
    )
    keyboard.adjust(2)
    return keyboard.as_markup()

# Меню управления автомобилями
def get_cars_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="📥 Добавить автомобиль", callback_data="cars_add"),
        InlineKeyboardButton(text="📋 Список автомобилей", callback_data="cars_list"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main")
    )
    keyboard.adjust(2)
    return keyboard.as_markup()

# Меню отчетов
def get_reports_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="📊 HTML отчет", callback_data="reports_html"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main")
    )
    return keyboard.as_markup()

# Меню обслуживания
def get_maintenance_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="➕ Добавить расход", callback_data="maintenance_add"),
        InlineKeyboardButton(text="📋 История обслуживания", callback_data="maintenance_list"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main")
    )
    keyboard.adjust(2)
    return keyboard.as_markup()

# Меню управления расходами
def get_expenses_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="📢 Рекламные расходы", callback_data="expenses_advertisement"),
        InlineKeyboardButton(text="📋 Прочие расходы", callback_data="expenses_other"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main")
    )
    keyboard.adjust(1)
    return keyboard.as_markup()

# Меню рекламных расходов
def get_advertisement_expenses_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="➕ Добавить расход", callback_data="add_advertisement_cost"),
        InlineKeyboardButton(text="📋 История расходов", callback_data="list_advertisement_costs"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_expenses")
    )
    keyboard.adjust(1)
    return keyboard.as_markup()

# Меню прочих расходов
def get_other_expenses_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="➕ Добавить расход", callback_data="add_other_cost"),
        InlineKeyboardButton(text="📋 История расходов", callback_data="list_other_costs"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_expenses")
    )
    keyboard.adjust(1)
    return keyboard.as_markup()

# Кнопка "Назад" в главное меню
def get_back_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main"))
    return keyboard.as_markup()

# Кнопка "Назад" к меню автомобилей
def get_back_to_cars_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_cars"))
    return keyboard.as_markup()

# Кнопка "Назад" к меню расходов
def get_back_to_expenses_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_expenses"))
    return keyboard.as_markup()

# Клавиатура для списка автомобилей
def get_cars_list_keyboard(cars, page=0, per_page=5):
    keyboard = InlineKeyboardBuilder()
    
    start_idx = page * per_page
    end_idx = start_idx + per_page
    paginated_cars = cars[start_idx:end_idx]
    
    for car in paginated_cars:
        status_icons = {
            'available': '✅',
            'rented': '🔵',
            'sold': '💰',
            'maintenance': '🛠️'
        }
        icon = status_icons.get(car['status'], '❓')
        
        keyboard.add(InlineKeyboardButton(
            text=f"{icon} {car['name']} ({car['license_plate']})",
            callback_data=f"car_detail_{car['id']}"
        ))
    
    # Пагинация
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад", 
            callback_data=f"cars_page_{page-1}"
        ))
    
    if end_idx < len(cars):
        navigation_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️", 
            callback_data=f"cars_page_{page+1}"
        ))
    
    if navigation_buttons:
        keyboard.add(*navigation_buttons)
    
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_cars"))
    keyboard.adjust(1)
    return keyboard.as_markup()

# Клавиатура для деталей автомобиля
def get_car_detail_keyboard(car_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="💰 Продать", callback_data=f"car_sell_{car_id}"),
        InlineKeyboardButton(text="❌ Удалить", callback_data=f"car_delete_{car_id}"),
        InlineKeyboardButton(text="🛠️ Обслуживание", callback_data=f"car_maintenance_{car_id}"),
        InlineKeyboardButton(text="🔙 К списку", callback_data="cars_list")
    )
    keyboard.adjust(2)
    return keyboard.as_markup()

# Клавиатура подтверждения удаления
def get_confirmation_keyboard(action, item_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}_{item_id}"),
        InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_{action}_{item_id}")
    )
    return keyboard.as_markup()

# Клавиатура для продажи автомобиля
def get_sell_car_keyboard(car_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="💰 Указать цену продажи", callback_data=f"car_set_sale_price_{car_id}"),
        InlineKeyboardButton(text="🔙 Назад", callback_data=f"car_detail_{car_id}")
    )
    return keyboard.as_markup()

# Клавиатура для выбора автомобиля для обслуживания
def get_cars_for_maintenance_keyboard(cars, page=0, per_page=5):
    keyboard = InlineKeyboardBuilder()
    
    start_idx = page * per_page
    end_idx = start_idx + per_page
    paginated_cars = cars[start_idx:end_idx]
    
    for car in paginated_cars:
        keyboard.add(InlineKeyboardButton(
            text=f"{car['name']} ({car['license_plate']})",
            callback_data=f"maintenance_for_car_{car['id']}"
        ))
    
    # Пагинация
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад", 
            callback_data=f"maintenance_cars_page_{page-1}"
        ))
    
    if end_idx < len(cars):
        navigation_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️", 
            callback_data=f"maintenance_cars_page_{page+1}"
        ))
    
    if navigation_buttons:
        keyboard.add(*navigation_buttons)
    
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_maintenance"))
    keyboard.adjust(1)
    return keyboard.as_markup()

# Клавиатура для истории обслуживания
def get_maintenance_list_keyboard(maintenance_records, page=0, per_page=5):
    keyboard = InlineKeyboardBuilder()
    
    start_idx = page * per_page
    end_idx = start_idx + per_page
    paginated_records = maintenance_records[start_idx:end_idx]
    
    for record in paginated_records:
        keyboard.add(InlineKeyboardButton(
            text=f"${record['amount']} - {record['description'][:30]}",
            callback_data=f"maintenance_detail_{record['id']}"
        ))
    
    # Пагинация
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад", 
            callback_data=f"maintenance_page_{page-1}"
        ))
    
    if end_idx < len(maintenance_records):
        navigation_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️", 
            callback_data=f"maintenance_page_{page+1}"
        ))
    
    if navigation_buttons:
        keyboard.add(*navigation_buttons)
    
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_maintenance"))
    keyboard.adjust(1)
    return keyboard.as_markup()

# Клавиатура для рекламных расходов
def get_advertisement_costs_keyboard(costs, page=0, per_page=5):
    keyboard = InlineKeyboardBuilder()
    
    start_idx = page * per_page
    end_idx = start_idx + per_page
    paginated_costs = costs[start_idx:end_idx]
    
    for cost in paginated_costs:
        keyboard.add(InlineKeyboardButton(
            text=f"${cost['amount']} - {cost['description'][:30]}",
            callback_data=f"advertisement_detail_{cost['id']}"
        ))
    
    # Пагинация
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад", 
            callback_data=f"advertisement_page_{page-1}"
        ))
    
    if end_idx < len(costs):
        navigation_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️", 
            callback_data=f"advertisement_page_{page+1}"
        ))
    
    if navigation_buttons:
        keyboard.add(*navigation_buttons)
    
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="expenses_advertisement"))
    keyboard.adjust(1)
    return keyboard.as_markup()

# Клавиатура для прочих расходов
def get_other_costs_keyboard(costs, page=0, per_page=5):
    keyboard = InlineKeyboardBuilder()
    
    start_idx = page * per_page
    end_idx = start_idx + per_page
    paginated_costs = costs[start_idx:end_idx]
    
    for cost in paginated_costs:
        keyboard.add(InlineKeyboardButton(
            text=f"${cost['amount']} - {cost['description'][:30]}",
            callback_data=f"other_cost_detail_{cost['id']}"
        ))
    
    # Пагинация
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад", 
            callback_data=f"other_costs_page_{page-1}"
        ))
    
    if end_idx < len(costs):
        navigation_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️", 
            callback_data=f"other_costs_page_{page+1}"
        ))
    
    if navigation_buttons:
        keyboard.add(*navigation_buttons)
    
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="expenses_other"))
    keyboard.adjust(1)
    return keyboard.as_markup()