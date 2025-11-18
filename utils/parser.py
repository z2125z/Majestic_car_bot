import re
from typing import Dict, Optional

def parse_rental_message(text: str) -> Optional[Dict]:
    """
    Парсит сообщение о аренде транспорта и возвращает структурированные данные
    """
    patterns = {
        'server': r'Сервер:\s*(.+)',
        'character': r'Персонаж:\s*(.+)',
        'transport': r'Транспорт:\s*(.+)',
        'license_plate': r'Номер транспорта:\s*([A-Z0-9]+)',
        'price': r'Цена:\s*\$?\s*([\d\s,]+)',
        'duration': r'Длительность:\s*(.+)',
        'renter': r'Арендатор:\s*(.+)'
    }
    
    result = {}
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            result[key] = match.group(1).strip()
    
    # Преобразуем цену в число (исправляем проблему с пробелами)
    if 'price' in result:
        # Убираем пробелы и запятые, затем преобразуем в число
        price_cleaned = result['price'].replace(' ', '').replace(',', '')
        try:
            result['price'] = float(price_cleaned)
        except ValueError:
            # Если не удалось преобразовать, попробуем извлечь цифры
            numbers = re.findall(r'\d+', result['price'])
            if numbers:
                result['price'] = float(''.join(numbers))
            else:
                result['price'] = 0
    
    # Проверяем, что все обязательные поля найдены
    required_fields = ['server', 'character', 'transport', 'license_plate', 'price', 'duration', 'renter']
    if all(field in result for field in required_fields):
        return result
    
    return None