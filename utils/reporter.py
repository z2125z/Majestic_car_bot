from jinja2 import Template
import aiofiles
from datetime import datetime
from database.models import db

async def generate_html_report() -> str:
    """
    Генерирует полную HTML страницу со всей статистикой
    """
    # Получаем все данные
    rentals = db.get_all_rentals()
    cars = db.get_all_cars()
    maintenance = db.get_all_maintenance()
    advertisement_costs = db.get_all_advertisement_costs()
    other_costs = db.get_all_other_costs()
    
    # Получаем финансовую статистику
    financial_stats = db.get_financial_stats()
    expense_stats = db.get_expense_stats()
    server_stats = db.get_server_stats()
    transport_stats = db.get_transport_stats()
    cars_stats = db.get_cars_stats()
    
    # Основная статистика
    total_income = financial_stats.get('rental_income', 0)
    total_sales = financial_stats.get('sales_income', 0)
    total_revenue = financial_stats.get('total_income', 0)
    net_profit = financial_stats.get('net_profit', 0)
    profitability = financial_stats.get('profitability', 0)
    
    # Расходы
    expenses = expense_stats.get('expenses', {})
    maintenance_total = expenses.get('maintenance', 0)
    advertisement_total = expenses.get('advertisement', 0)
    other_costs_total = expenses.get('other_costs', 0)
    car_costs_total = expenses.get('car_costs', 0)
    total_expenses = expenses.get('total', 0)
    
    # Проценты расходов
    maintenance_percent = expense_stats.get('maintenance_percent', 0)
    advertisement_percent = expense_stats.get('advertisement_percent', 0)
    other_costs_percent = expense_stats.get('other_costs_percent', 0)
    car_costs_percent = expense_stats.get('car_costs_percent', 0)
    expense_income_ratio = expense_stats.get('expense_income_ratio', 0)
    
    # Статистика по автомобилям
    total_cars = cars_stats.get('total_cars', 0)
    status_stats = cars_stats.get('status_stats', {})
    cars_total_income = cars_stats.get('total_income', 0)
    cars_total_rentals = cars_stats.get('total_rentals', 0)
    
    # Статистика по серверам
    servers_income = 0
    servers_count = 0
    for server_data in server_stats.values():
        servers_income += server_data.get('income', 0)
        servers_count += server_data.get('count', 0)
    
    # Статистика по транспорту
    transport_income = 0
    transport_count = 0
    for transport_data in transport_stats.values():
        transport_income += transport_data.get('income', 0)
        transport_count += transport_data.get('count', 0)
    
    html_template = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Полная статистика аренды транспорта</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .header {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                text-align: center;
                margin-bottom: 30px;
            }
            
            .header h1 {
                color: #2c3e50;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header .subtitle {
                color: #7f8c8d;
                font-size: 1.2em;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                text-align: center;
                transition: transform 0.3s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
            }
            
            .stat-card.income {
                border-left: 5px solid #2ecc71;
            }
            
            .stat-card.expense {
                border-left: 5px solid #e74c3c;
            }
            
            .stat-card.profit {
                border-left: 5px solid #3498db;
            }
            
            .stat-card.info {
                border-left: 5px solid #f39c12;
            }
            
            .stat-value {
                font-size: 2.5em;
                font-weight: bold;
                margin: 10px 0;
            }
            
            .stat-income { color: #27ae60; }
            .stat-expense { color: #c0392b; }
            .stat-profit { color: #2980b9; }
            .stat-neutral { color: #7f8c8d; }
            
            .stat-label {
                font-size: 1.1em;
                color: #7f8c8d;
                margin-bottom: 5px;
            }
            
            .section {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            
            .section h2 {
                color: #2c3e50;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #ecf0f1;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }
            
            th, td {
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #ecf0f1;
            }
            
            th {
                background-color: #34495e;
                color: white;
                font-weight: 600;
            }
            
            tr:hover {
                background-color: #f8f9fa;
            }
            
            .progress-bar {
                background-color: #ecf0f1;
                border-radius: 10px;
                height: 20px;
                margin: 10px 0;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                border-radius: 10px;
                transition: width 0.3s ease;
            }
            
            .progress-maintenance { background-color: #e67e22; }
            .progress-advertisement { background-color: #9b59b6; }
            .progress-other { background-color: #34495e; }
            .progress-cars { background-color: #e74c3c; }
            
            .financial-summary {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-top: 20px;
            }
            
            @media (max-width: 768px) {
                .financial-summary {
                    grid-template-columns: 1fr;
                }
                
                .stats-grid {
                    grid-template-columns: 1fr;
                }
            }
            
            .positive { color: #27ae60; font-weight: bold; }
            .negative { color: #e74c3c; font-weight: bold; }
            .neutral { color: #f39c12; font-weight: bold; }
            
            .summary-item {
                display: flex;
                justify-content: space-between;
                margin: 10px 0;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 8px;
            }
            
            .summary-label {
                font-weight: 600;
                color: #2c3e50;
            }
            
            .summary-value {
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Полная статистика аренды транспорта</h1>
                <div class="subtitle">Отчет сгенерирован: {{ current_time }}</div>
            </div>
            
            <!-- Основные метрики -->
            <div class="stats-grid">
                <div class="stat-card income">
                    <div class="stat-label">💰 Общий доход</div>
                    <div class="stat-value stat-income">${{ "%.2f"|format(total_revenue) }}</div>
                    <div>Аренды: ${{ "%.2f"|format(total_income) }} | Продажи: ${{ "%.2f"|format(total_sales) }}</div>
                </div>
                
                <div class="stat-card expense">
                    <div class="stat-label">💸 Общие расходы</div>
                    <div class="stat-value stat-expense">${{ "%.2f"|format(total_expenses) }}</div>
                    <div>Соотношение: {{ "%.1f"|format(expense_income_ratio) }}%</div>
                </div>
                
                <div class="stat-card profit">
                    <div class="stat-label">💎 Чистая прибыль</div>
                    <div class="stat-value {% if net_profit >= 0 %}stat-profit{% else %}stat-expense{% endif %}">
                        ${{ "%.2f"|format(net_profit) }}
                    </div>
                    <div>Рентабельность: {{ "%.1f"|format(profitability) }}%</div>
                </div>
                
                <div class="stat-card info">
                    <div class="stat-label">🚗 Автомобили</div>
                    <div class="stat-value stat-neutral">{{ total_cars }}</div>
                    <div>Аренд: {{ cars_total_rentals }} | Доход: ${{ "%.2f"|format(cars_total_income) }}</div>
                </div>
            </div>
            
            <!-- Финансовая сводка -->
            <div class="section">
                <h2>💰 Финансовая сводка</h2>
                <div class="financial-summary">
                    <div>
                        <h3>📈 Доходы</h3>
                        <div class="summary-item">
                            <span class="summary-label">Доход от аренд:</span>
                            <span class="summary-value positive">${{ "%.2f"|format(total_income) }}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Доход от продаж:</span>
                            <span class="summary-value positive">${{ "%.2f"|format(total_sales) }}</span>
                        </div>
                        <div class="summary-item" style="background: #e8f5e8; font-weight: bold;">
                            <span class="summary-label">Общий доход:</span>
                            <span class="summary-value positive">${{ "%.2f"|format(total_revenue) }}</span>
                        </div>
                    </div>
                    
                    <div>
                        <h3>📉 Расходы</h3>
                        <div class="summary-item">
                            <span class="summary-label">Обслуживание:</span>
                            <span class="summary-value negative">${{ "%.2f"|format(maintenance_total) }}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Реклама:</span>
                            <span class="summary-value negative">${{ "%.2f"|format(advertisement_total) }}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Прочие расходы:</span>
                            <span class="summary-value negative">${{ "%.2f"|format(other_costs_total) }}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Автомобили:</span>
                            <span class="summary-value negative">${{ "%.2f"|format(car_costs_total) }}</span>
                        </div>
                        <div class="summary-item" style="background: #ffeaea; font-weight: bold;">
                            <span class="summary-label">Общие расходы:</span>
                            <span class="summary-value negative">${{ "%.2f"|format(total_expenses) }}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Детализация расходов -->
            <div class="section">
                <h2>💸 Детализация расходов</h2>
                <table>
                    <tr>
                        <th>Тип расхода</th>
                        <th>Сумма</th>
                        <th>Процент от общих расходов</th>
                        <th>Прогресс</th>
                    </tr>
                    <tr>
                        <td>🛠️ Обслуживание</td>
                        <td>${{ "%.2f"|format(maintenance_total) }}</td>
                        <td>{{ "%.1f"|format(maintenance_percent) }}%</td>
                        <td>
                            <div class="progress-bar">
                                <div class="progress-fill progress-maintenance" style="width: {{ maintenance_percent }}%"></div>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td>📢 Реклама</td>
                        <td>${{ "%.2f"|format(advertisement_total) }}</td>
                        <td>{{ "%.1f"|format(advertisement_percent) }}%</td>
                        <td>
                            <div class="progress-bar">
                                <div class="progress-fill progress-advertisement" style="width: {{ advertisement_percent }}%"></div>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td>📋 Прочие расходы</td>
                        <td>${{ "%.2f"|format(other_costs_total) }}</td>
                        <td>{{ "%.1f"|format(other_costs_percent) }}%</td>
                        <td>
                            <div class="progress-bar">
                                <div class="progress-fill progress-other" style="width: {{ other_costs_percent }}%"></div>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td>🚗 Автомобили</td>
                        <td>${{ "%.2f"|format(car_costs_total) }}</td>
                        <td>{{ "%.1f"|format(car_costs_percent) }}%</td>
                        <td>
                            <div class="progress-bar">
                                <div class="progress-fill progress-cars" style="width: {{ car_costs_percent }}%"></div>
                            </div>
                        </td>
                    </tr>
                </table>
            </div>
            
            <!-- Статистика по серверам -->
            <div class="section">
                <h2>🌐 Статистика по серверам</h2>
                <table>
                    <tr>
                        <th>Сервер</th>
                        <th>Количество аренд</th>
                        <th>Доход</th>
                        <th>Средний чек</th>
                    </tr>
                    {% for server, data in server_stats.items() %}
                    <tr>
                        <td>{{ server }}</td>
                        <td>{{ data.count }}</td>
                        <td>${{ "%.2f"|format(data.income) }}</td>
                        <td>${{ "%.2f"|format(data.income / data.count) if data.count > 0 else 0 }}</td>
                    </tr>
                    {% endfor %}
                    <tr style="font-weight: bold; background-color: #f8f9fa;">
                        <td>Итого</td>
                        <td>{{ servers_count }}</td>
                        <td>${{ "%.2f"|format(servers_income) }}</td>
                        <td>${{ "%.2f"|format(servers_income / servers_count) if servers_count > 0 else 0 }}</td>
                    </tr>
                </table>
            </div>
            
            <!-- Статистика по транспорту -->
            <div class="section">
                <h2>🚗 Статистика по транспорту</h2>
                <table>
                    <tr>
                        <th>Транспорт</th>
                        <th>Количество аренд</th>
                        <th>Доход</th>
                        <th>Средний чек</th>
                    </tr>
                    {% for transport, data in transport_stats.items() %}
                    <tr>
                        <td>{{ transport }}</td>
                        <td>{{ data.count }}</td>
                        <td>${{ "%.2f"|format(data.income) }}</td>
                        <td>${{ "%.2f"|format(data.income / data.count) if data.count > 0 else 0 }}</td>
                    </tr>
                    {% endfor %}
                    <tr style="font-weight: bold; background-color: #f8f9fa;">
                        <td>Итого</td>
                        <td>{{ transport_count }}</td>
                        <td>${{ "%.2f"|format(transport_income) }}</td>
                        <td>${{ "%.2f"|format(transport_income / transport_count) if transport_count > 0 else 0 }}</td>
                    </tr>
                </table>
            </div>
            
            <!-- Статусы автомобилей -->
            <div class="section">
                <h2>📊 Статусы автомобилей</h2>
                <table>
                    <tr>
                        <th>Статус</th>
                        <th>Количество</th>
                        <th>Процент</th>
                    </tr>
                    {% for status, count in status_stats.items() %}
                    <tr>
                        <td>
                            {% if status == 'available' %}✅ Доступен
                            {% elif status == 'rented' %}🔵 В аренде
                            {% elif status == 'sold' %}💰 Продан
                            {% elif status == 'maintenance' %}🛠️ На обслуживании
                            {% else %}{{ status }}{% endif %}
                        </td>
                        <td>{{ count }}</td>
                        <td>{{ "%.1f"|format((count / total_cars * 100) if total_cars > 0 else 0) }}%</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <!-- История обслуживания -->
            <div class="section">
                <h2>🛠️ История обслуживания</h2>
                {% if maintenance %}
                <table>
                    <tr>
                        <th>Автомобиль</th>
                        <th>Сумма</th>
                        <th>Описание</th>
                        <th>Дата</th>
                    </tr>
                    {% for record in maintenance[:10] %}
                    <tr>
                        <td>{{ record.car_name }} ({{ record.license_plate }})</td>
                        <td>${{ "%.2f"|format(record.amount) }}</td>
                        <td>{{ record.description }}</td>
                        <td>{{ record.maintenance_date }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% if maintenance|length > 10 %}
                <p style="text-align: center; margin-top: 15px; color: #7f8c8d;">
                    ... и еще {{ maintenance|length - 10 }} записей
                </p>
                {% endif %}
                {% else %}
                <p style="text-align: center; color: #7f8c8d;">Нет записей об обслуживании</p>
                {% endif %}
            </div>
            
            <!-- Последние аренды -->
            <div class="section">
                <h2>📝 Последние аренды</h2>
                {% if rentals %}
                <table>
                    <tr>
                        <th>Дата</th>
                        <th>Сервер</th>
                        <th>Транспорт</th>
                        <th>Номер</th>
                        <th>Цена</th>
                        <th>Арендатор</th>
                    </tr>
                    {% for rental in rentals[:15] %}
                    <tr>
                        <td>{{ rental.created_at[:16] }}</td>
                        <td>{{ rental.server }}</td>
                        <td>{{ rental.transport }}</td>
                        <td>{{ rental.license_plate }}</td>
                        <td>${{ "%.2f"|format(rental.price) }}</td>
                        <td>{{ rental.renter }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% if rentals|length > 15 %}
                <p style="text-align: center; margin-top: 15px; color: #7f8c8d;">
                    ... и еще {{ rentals|length - 15 }} аренд
                </p>
                {% endif %}
                {% else %}
                <p style="text-align: center; color: #7f8c8d;">Нет данных об арендах</p>
                {% endif %}
            </div>
            
            <!-- Футер -->
            <div class="section" style="text-align: center; background: #34495e; color: white;">
                <p>Отчет сгенерирован автоматически • Всего записей: {{ rentals|length }} аренд, {{ maintenance|length }} обслуживаний</p>
                <p>Рентабельность бизнеса: <span class="{% if profitability >= 20 %}positive{% elif profitability >= 0 %}neutral{% else %}negative{% endif %}">{{ "%.1f"|format(profitability) }}%</span></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    template = Template(html_template)
    html_content = template.render(
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        # Основные метрики
        total_income=total_income,
        total_sales=total_sales,
        total_revenue=total_revenue,
        net_profit=net_profit,
        profitability=profitability,
        total_expenses=total_expenses,
        expense_income_ratio=expense_income_ratio,
        total_cars=total_cars,
        cars_total_income=cars_total_income,
        cars_total_rentals=cars_total_rentals,
        
        # Расходы
        maintenance_total=maintenance_total,
        advertisement_total=advertisement_total,
        other_costs_total=other_costs_total,
        car_costs_total=car_costs_total,
        maintenance_percent=maintenance_percent,
        advertisement_percent=advertisement_percent,
        other_costs_percent=other_costs_percent,
        car_costs_percent=car_costs_percent,
        
        # Статистика
        server_stats=server_stats,
        transport_stats=transport_stats,
        status_stats=status_stats,
        
        # Данные
        rentals=rentals,
        maintenance=maintenance,
        advertisement_costs=advertisement_costs,
        other_costs=other_costs,
        cars=cars,
        
        # Суммарные счетчики
        servers_income=servers_income,
        servers_count=servers_count,
        transport_income=transport_income,
        transport_count=transport_count
    )
    
    # Сохраняем HTML файл
    filename = f"full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
        await f.write(html_content)
    
    return filename