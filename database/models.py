import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self, db_path="rentals.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            # Таблица аренд
            conn.execute('''
                CREATE TABLE IF NOT EXISTS rentals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server TEXT NOT NULL,
                    character TEXT NOT NULL,
                    transport TEXT NOT NULL,
                    license_plate TEXT NOT NULL,
                    price REAL NOT NULL,
                    duration TEXT NOT NULL,
                    renter TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица автомобилей
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    license_plate TEXT UNIQUE NOT NULL,
                    status TEXT DEFAULT 'available',
                    purchase_price REAL DEFAULT 0,
                    purchase_date TIMESTAMP,
                    sale_price REAL,
                    sale_date TIMESTAMP,
                    total_income REAL DEFAULT 0,
                    total_rentals INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица расходов на обслуживание
            conn.execute('''
                CREATE TABLE IF NOT EXISTS maintenance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    car_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT NOT NULL,
                    maintenance_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (car_id) REFERENCES cars (id) ON DELETE CASCADE
                )
            ''')
            
            # Таблица расходов на рекламу и объявления
            conn.execute('''
                CREATE TABLE IF NOT EXISTS advertisement_costs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    description TEXT NOT NULL,
                    advertisement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица прочих расходов
            conn.execute('''
                CREATE TABLE IF NOT EXISTS other_costs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    description TEXT NOT NULL,
                    cost_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    # === МЕТОДЫ ДЛЯ АРЕНД ===
    
    def add_rental(self, rental_data: Dict[str, Any]) -> bool:
        """Добавление записи об аренде с автоматическим созданием автомобиля"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Приводим license_plate к верхнему регистру
                license_plate = rental_data['license_plate'].upper()
                
                # Проверяем, есть ли автомобиль в базе
                cursor.execute('SELECT id FROM cars WHERE license_plate = ?', (license_plate,))
                car = cursor.fetchone()
                
                if car:
                    car_id = car['id']
                else:
                    # Создаем новый автомобиль
                    cursor.execute('''
                        INSERT INTO cars (name, license_plate, purchase_price, purchase_date)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        rental_data['transport'],
                        license_plate,
                        0,  # Цена покупки неизвестна
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                    car_id = cursor.lastrowid
                    print(f"Создан новый автомобиль: {rental_data['transport']} ({license_plate})")
                
                # Обновляем статистику автомобиля
                cursor.execute('''
                    UPDATE cars 
                    SET total_income = total_income + ?, 
                        total_rentals = total_rentals + 1,
                        status = 'rented'
                    WHERE id = ?
                ''', (rental_data['price'], car_id))
                
                # Добавляем запись об аренде
                cursor.execute('''
                    INSERT INTO rentals 
                    (server, character, transport, license_plate, price, duration, renter)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    rental_data['server'],
                    rental_data['character'],
                    rental_data['transport'],
                    license_plate,
                    rental_data['price'],
                    rental_data['duration'],
                    rental_data['renter']
                ))
                
                conn.commit()
                print(f"Аренда успешно сохранена: {rental_data['transport']} ({license_plate}) - ${rental_data['price']}")
                return True
                
        except Exception as e:
            print(f"Ошибка базы данных в add_rental: {e}")
            return False
    
    def get_all_rentals(self) -> List[Dict[str, Any]]:
        """Получение всех записей об арендах"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM rentals ORDER BY created_at DESC
                ''')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Ошибка базы данных в get_all_rentals: {e}")
            return []
    
    def get_rentals_by_car(self, license_plate: str) -> List[Dict[str, Any]]:
        """Получение аренд по номеру автомобиля"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM rentals 
                    WHERE license_plate = ? 
                    ORDER BY created_at DESC
                ''', (license_plate.upper(),))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Ошибка базы данных в get_rentals_by_car: {e}")
            return []
    
    def get_rentals_count(self) -> int:
        """Получение общего количества аренд"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM rentals')
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Ошибка базы данных в get_rentals_count: {e}")
            return 0
    
    # === МЕТОДЫ ДЛЯ АВТОМОБИЛЕЙ ===
    
    def add_car(self, name: str, license_plate: str, purchase_price: float = 0) -> bool:
        """Добавление автомобиля"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO cars (name, license_plate, purchase_price, purchase_date)
                    VALUES (?, ?, ?, ?)
                ''', (name, license_plate.upper(), purchase_price, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                print(f"Автомобиль добавлен: {name} ({license_plate})")
                return True
        except sqlite3.IntegrityError:
            print(f"Автомобиль с номером {license_plate} уже существует")
            return False
        except Exception as e:
            print(f"Ошибка базы данных в add_car: {e}")
            return False
    
    def get_car(self, license_plate: str) -> Optional[Dict[str, Any]]:
        """Получение автомобиля по номеру"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM cars WHERE license_plate = ?', (license_plate.upper(),))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Ошибка базы данных в get_car: {e}")
            return None
    
    def get_car_by_id(self, car_id: int) -> Optional[Dict[str, Any]]:
        """Получение автомобиля по ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM cars WHERE id = ?', (car_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Ошибка базы данных в get_car_by_id: {e}")
            return None
    
    def get_all_cars(self) -> List[Dict[str, Any]]:
        """Получение всех автомобилей"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM cars ORDER BY created_at DESC')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Ошибка базы данных в get_all_cars: {e}")
            return []
    
    def get_available_cars(self) -> List[Dict[str, Any]]:
        """Получение доступных автомобилей"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM cars WHERE status = "available" ORDER BY created_at DESC')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Ошибка базы данных в get_available_cars: {e}")
            return []
    
    def get_rented_cars(self) -> List[Dict[str, Any]]:
        """Получение арендованных автомобилей"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM cars WHERE status = "rented" ORDER BY created_at DESC')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Ошибка базы данных в get_rented_cars: {e}")
            return []
    
    def get_sold_cars(self) -> List[Dict[str, Any]]:
        """Получение проданных автомобилей"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM cars WHERE status = "sold" ORDER BY created_at DESC')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Ошибка базы данных в get_sold_cars: {e}")
            return []
    
    def update_car_status(self, license_plate: str, status: str) -> bool:
        """Обновление статуса автомобиля"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE cars SET status = ? WHERE license_plate = ?
                ''', (status, license_plate.upper()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка базы данных в update_car_status: {e}")
            return False
    
    def update_car(self, license_plate: str, name: str = None, purchase_price: float = None) -> bool:
        """Обновление информации об автомобиле"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                updates = []
                params = []
                
                if name:
                    updates.append("name = ?")
                    params.append(name)
                
                if purchase_price is not None:
                    updates.append("purchase_price = ?")
                    params.append(purchase_price)
                
                if updates:
                    params.append(license_plate.upper())
                    query = f"UPDATE cars SET {', '.join(updates)} WHERE license_plate = ?"
                    conn.execute(query, params)
                    conn.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка базы данных в update_car: {e}")
            return False
    
    def sell_car(self, license_plate: str, sale_price: float) -> bool:
        """Продажа автомобиля"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE cars SET status = 'sold', sale_price = ?, sale_date = ?
                    WHERE license_plate = ?
                ''', (sale_price, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), license_plate.upper()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка базы данных в sell_car: {e}")
            return False
    
    def delete_car(self, license_plate: str) -> bool:
        """Удаление автомобиля"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Сначала удаляем связанные записи обслуживания
                car = self.get_car(license_plate)
                if car:
                    cursor.execute('DELETE FROM maintenance WHERE car_id = ?', (car['id'],))
                
                # Затем удаляем сам автомобиль
                cursor.execute('DELETE FROM cars WHERE license_plate = ?', (license_plate.upper(),))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка базы данных в delete_car: {e}")
            return False
    
    def get_cars_count(self) -> int:
        """Получение общего количества автомобилей"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM cars')
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Ошибка базы данных в get_cars_count: {e}")
            return 0
    
    def get_cars_stats(self) -> Dict[str, Any]:
        """Получение статистики по автомобилям"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Общее количество автомобилей
                cursor.execute('SELECT COUNT(*) FROM cars')
                total_cars = cursor.fetchone()[0]
                
                # Количество по статусам
                cursor.execute('SELECT status, COUNT(*) FROM cars GROUP BY status')
                status_stats = dict(cursor.fetchall())
                
                # Общий доход от аренд
                cursor.execute('SELECT SUM(total_income) FROM cars')
                total_income = cursor.fetchone()[0] or 0
                
                # Общее количество аренд
                cursor.execute('SELECT SUM(total_rentals) FROM cars')
                total_rentals = cursor.fetchone()[0] or 0
                
                return {
                    'total_cars': total_cars,
                    'status_stats': status_stats,
                    'total_income': total_income,
                    'total_rentals': total_rentals
                }
        except Exception as e:
            print(f"Ошибка базы данных в get_cars_stats: {e}")
            return {}
    
    # === МЕТОДЫ ДЛЯ ОБСЛУЖИВАНИЯ ===
    
    def add_maintenance(self, car_id: int, amount: float, description: str) -> bool:
        """Добавление записи об обслуживании"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO maintenance (car_id, amount, description, maintenance_date)
                    VALUES (?, ?, ?, ?)
                ''', (car_id, amount, description, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка базы данных в add_maintenance: {e}")
            return False
    
    def get_car_maintenance(self, car_id: int) -> List[Dict[str, Any]]:
        """Получение истории обслуживания автомобиля"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM maintenance 
                    WHERE car_id = ? 
                    ORDER BY maintenance_date DESC
                ''', (car_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Ошибка базы данных в get_car_maintenance: {e}")
            return []
    
    def get_all_maintenance(self) -> List[Dict[str, Any]]:
        """Получение всей истории обслуживания"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT m.*, c.name as car_name, c.license_plate 
                    FROM maintenance m
                    JOIN cars c ON m.car_id = c.id
                    ORDER BY m.maintenance_date DESC
                ''')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Ошибка базы данных в get_all_maintenance: {e}")
            return []
    
    def get_maintenance_total(self) -> float:
        """Получение общей суммы расходов на обслуживание"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(amount) FROM maintenance')
                result = cursor.fetchone()[0]
                return result if result else 0.0
        except Exception as e:
            print(f"Ошибка базы данных в get_maintenance_total: {e}")
            return 0.0
    
    def get_maintenance_by_car(self, car_id: int) -> List[Dict[str, Any]]:
        """Получение обслуживания по ID автомобиля"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT m.*, c.name as car_name, c.license_plate 
                    FROM maintenance m
                    JOIN cars c ON m.car_id = c.id
                    WHERE m.car_id = ?
                    ORDER BY m.maintenance_date DESC
                ''', (car_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Ошибка базы данных в get_maintenance_by_car: {e}")
            return []
    
    # === МЕТОДЫ ДЛЯ РАСХОДОВ НА РЕКЛАМУ ===
    
    def add_advertisement_cost(self, amount: float, description: str) -> bool:
        """Добавление расхода на рекламу"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO advertisement_costs (amount, description, advertisement_date)
                    VALUES (?, ?, ?)
                ''', (amount, description, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка базы данных в add_advertisement_cost: {e}")
            return False
    
    def get_all_advertisement_costs(self) -> List[Dict[str, Any]]:
        """Получение всех расходов на рекламу"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM advertisement_costs 
                    ORDER BY advertisement_date DESC
                ''')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Ошибка базы данных в get_all_advertisement_costs: {e}")
            return []
    
    def get_advertisement_costs_total(self) -> float:
        """Получение общей суммы расходов на рекламу"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(amount) FROM advertisement_costs')
                result = cursor.fetchone()[0]
                return result if result else 0.0
        except Exception as e:
            print(f"Ошибка базы данных в get_advertisement_costs_total: {e}")
            return 0.0
    
    def delete_advertisement_cost(self, cost_id: int) -> bool:
        """Удаление расхода на рекламу"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM advertisement_costs WHERE id = ?', (cost_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка базы данных в delete_advertisement_cost: {e}")
            return False
    
    # === МЕТОДЫ ДЛЯ ПРОЧИХ РАСХОДОВ ===
    
    def add_other_cost(self, amount: float, description: str) -> bool:
        """Добавление прочего расхода"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO other_costs (amount, description, cost_date)
                    VALUES (?, ?, ?)
                ''', (amount, description, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка базы данных в add_other_cost: {e}")
            return False
    
    def get_all_other_costs(self) -> List[Dict[str, Any]]:
        """Получение всех прочих расходов"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM other_costs 
                    ORDER BY cost_date DESC
                ''')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Ошибка базы данных в get_all_other_costs: {e}")
            return []
    
    def get_other_costs_total(self) -> float:
        """Получение общей суммы прочих расходов"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(amount) FROM other_costs')
                result = cursor.fetchone()[0]
                return result if result else 0.0
        except Exception as e:
            print(f"Ошибка базы данных в get_other_costs_total: {e}")
            return 0.0
    
    def delete_other_cost(self, cost_id: int) -> bool:
        """Удаление прочего расхода"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM other_costs WHERE id = ?', (cost_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка базы данных в delete_other_cost: {e}")
            return False
    
    # === ФИНАНСОВЫЕ МЕТОДЫ ===
    
    def get_total_income(self) -> float:
        """Получение общего дохода от аренд"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(price) FROM rentals')
                result = cursor.fetchone()[0]
                return result if result else 0.0
        except Exception as e:
            print(f"Ошибка базы данных в get_total_income: {e}")
            return 0.0
    
    def get_total_car_costs(self) -> float:
        """Получение общей стоимости автомобилей"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(purchase_price) FROM cars')
                result = cursor.fetchone()[0]
                return result if result else 0.0
        except Exception as e:
            print(f"Ошибка базы данных в get_total_car_costs: {e}")
            return 0.0
    
    def get_total_sales_income(self) -> float:
        """Получение общего дохода от продаж"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(sale_price) FROM cars WHERE sale_price IS NOT NULL')
                result = cursor.fetchone()[0]
                return result if result else 0.0
        except Exception as e:
            print(f"Ошибка базы данных в get_total_sales_income: {e}")
            return 0.0
    
    def get_total_expenses(self) -> Dict[str, float]:
        """Получение всех расходов"""
        try:
            maintenance_total = self.get_maintenance_total()
            advertisement_total = self.get_advertisement_costs_total()
            other_costs_total = self.get_other_costs_total()
            car_costs = self.get_total_car_costs()
            
            total_expenses = maintenance_total + advertisement_total + other_costs_total + car_costs
            
            return {
                'maintenance': maintenance_total,
                'advertisement': advertisement_total,
                'other_costs': other_costs_total,
                'car_costs': car_costs,
                'total': total_expenses
            }
        except Exception as e:
            print(f"Ошибка базы данных в get_total_expenses: {e}")
            return {
                'maintenance': 0.0,
                'advertisement': 0.0,
                'other_costs': 0.0,
                'car_costs': 0.0,
                'total': 0.0
            }
    
    def get_financial_stats(self) -> Dict[str, Any]:
        """Получение полной финансовой статистики"""
        try:
            rental_income = self.get_total_income()
            sales_income = self.get_total_sales_income()
            expenses = self.get_total_expenses()
            
            total_income = rental_income + sales_income
            total_expenses = expenses['total']
            net_profit = total_income - total_expenses
            
            profitability = (net_profit / total_income * 100) if total_income > 0 else 0
            
            return {
                'rental_income': rental_income,
                'sales_income': sales_income,
                'total_income': total_income,
                'expenses': expenses,
                'net_profit': net_profit,
                'profitability': profitability,
                'total_rentals': self.get_rentals_count(),
                'total_cars': self.get_cars_count()
            }
        except Exception as e:
            print(f"Ошибка базы данных в get_financial_stats: {e}")
            return {}
    
    # === СТАТИСТИЧЕСКИЕ МЕТОДЫ ===
    
    def get_server_stats(self) -> Dict[str, Dict[str, Any]]:
        """Получение статистики по серверам"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT server, COUNT(*) as count, SUM(price) as income
                    FROM rentals 
                    GROUP BY server
                    ORDER BY income DESC
                ''')
                rows = cursor.fetchall()
                
                stats = {}
                for row in rows:
                    stats[row['server']] = {
                        'count': row['count'],
                        'income': row['income'] or 0
                    }
                return stats
        except Exception as e:
            print(f"Ошибка базы данных в get_server_stats: {e}")
            return {}
    
    def get_transport_stats(self) -> Dict[str, Dict[str, Any]]:
        """Получение статистики по типам транспорта"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT transport, COUNT(*) as count, SUM(price) as income
                    FROM rentals 
                    GROUP BY transport
                    ORDER BY income DESC
                ''')
                rows = cursor.fetchall()
                
                stats = {}
                for row in rows:
                    stats[row['transport']] = {
                        'count': row['count'],
                        'income': row['income'] or 0
                    }
                return stats
        except Exception as e:
            print(f"Ошибка базы данных в get_transport_stats: {e}")
            return {}
    
    def get_recent_rentals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение последних аренд"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM rentals 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Ошибка базы данных в get_recent_rentals: {e}")
            return []
    
    def get_top_cars_by_income(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Получение топ автомобилей по доходу"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM cars 
                    ORDER BY total_income DESC 
                    LIMIT ?
                ''', (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Ошибка базы данных в get_top_cars_by_income: {e}")
            return []
    
    def get_expense_stats(self) -> Dict[str, Any]:
        """Получение статистики по расходам"""
        try:
            expenses = self.get_total_expenses()
            total_income = self.get_total_income() + self.get_total_sales_income()
            
            # Расчет процентов от общих расходов
            if expenses['total'] > 0:
                maintenance_percent = (expenses['maintenance'] / expenses['total']) * 100
                advertisement_percent = (expenses['advertisement'] / expenses['total']) * 100
                other_costs_percent = (expenses['other_costs'] / expenses['total']) * 100
                car_costs_percent = (expenses['car_costs'] / expenses['total']) * 100
            else:
                maintenance_percent = advertisement_percent = other_costs_percent = car_costs_percent = 0
            
            # Процент расходов от доходов
            expense_income_ratio = (expenses['total'] / total_income * 100) if total_income > 0 else 0
            
            return {
                'expenses': expenses,
                'maintenance_percent': maintenance_percent,
                'advertisement_percent': advertisement_percent,
                'other_costs_percent': other_costs_percent,
                'car_costs_percent': car_costs_percent,
                'expense_income_ratio': expense_income_ratio,
                'total_income': total_income
            }
        except Exception as e:
            print(f"Ошибка базы данных в get_expense_stats: {e}")
            return {}

# Глобальный экземпляр базы данных
db = Database()