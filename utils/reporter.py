from jinja2 import Template
import aiofiles
from datetime import datetime

async def generate_html_report(rentals: list) -> str:
    """
    Генерирует HTML страницу со статистикой
    """
    # Статистика
    total_income = sum(rental['price'] for rental in rentals)
    total_rentals = len(rentals)
    
    # Статистика по серверам
    servers = {}
    for rental in rentals:
        server = rental['server']
        if server not in servers:
            servers[server] = {'count': 0, 'income': 0}
        servers[server]['count'] += 1
        servers[server]['income'] += rental['price']
    
    # Статистика по транспорту
    transport_stats = {}
    for rental in rentals:
        transport = rental['transport']
        if transport not in transport_stats:
            transport_stats[transport] = {'count': 0, 'income': 0}
        transport_stats[transport]['count'] += 1
        transport_stats[transport]['income'] += rental['price']
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Статистика аренды транспорта</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .stats { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #4CAF50; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .summary { font-size: 1.2em; font-weight: bold; color: #2c3e50; }
        </style>
    </head>
    <body>
        <h1>📊 Статистика аренды транспорта</h1>
        
        <div class="stats summary">
            💰 Общий доход: ${{ "%.2f"|format(total_income) }} | 🚗 Всего аренд: {{ total_rentals }}
        </div>
        
        <h2>📈 Статистика по серверам</h2>
        <table>
            <tr>
                <th>Сервер</th>
                <th>Количество аренд</th>
                <th>Доход</th>
            </tr>
            {% for server, data in servers.items() %}
            <tr>
                <td>{{ server }}</td>
                <td>{{ data.count }}</td>
                <td>${{ "%.2f"|format(data.income) }}</td>
            </tr>
            {% endfor %}
        </table>
        
        <h2>🚗 Статистика по транспорту</h2>
        <table>
            <tr>
                <th>Транспорт</th>
                <th>Количество аренд</th>
                <th>Доход</th>
            </tr>
            {% for transport, data in transport_stats.items() %}
            <tr>
                <td>{{ transport }}</td>
                <td>{{ data.count }}</td>
                <td>${{ "%.2f"|format(data.income) }}</td>
            </tr>
            {% endfor %}
        </table>
        
        <h2>📝 История аренд</h2>
        <table>
            <tr>
                <th>Дата</th>
                <th>Сервер</th>
                <th>Персонаж</th>
                <th>Транспорт</th>
                <th>Номер</th>
                <th>Цена</th>
                <th>Арендатор</th>
            </tr>
            {% for rental in rentals %}
            <tr>
                <td>{{ rental.created_at }}</td>
                <td>{{ rental.server }}</td>
                <td>{{ rental.character }}</td>
                <td>{{ rental.transport }}</td>
                <td>{{ rental.license_plate }}</td>
                <td>${{ "%.2f"|format(rental.price) }}</td>
                <td>{{ rental.renter }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    
    template = Template(html_template)
    html_content = template.render(
        rentals=rentals,
        total_income=total_income,
        total_rentals=total_rentals,
        servers=servers,
        transport_stats=transport_stats
    )
    
    # Сохраняем HTML файл
    filename = f"rental_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
        await f.write(html_content)
    
    return filename