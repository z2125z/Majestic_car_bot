import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any

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
                    status TEXT DEFAULT 'available', -- available, rented, sold, maintenance
                    purchase_price REAL,
                    purchase_date TIMESTAMP,
                    sale_price REAL,
                    sale_date TIMESTAMP,
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
                    FOREIGN KEY (car_id) REFERENCES cars (id)
                )
            ''')
            conn.commit()
    
    # === МЕТОДЫ ДЛЯ АРЕНД ===
    
    def add_rental(self, rental_data: Dict[str, Any]) -> bool:
        """Добавление записи об аренде"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO rentals 
                    (server, character, transport, license_plate, price, duration, renter)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    rental_data['server'],
                    rental_data['character'],
                    rental_data['transport'],
                    rental_data['license_plate'],
                    rental_data['price'],
                    rental_data['duration'],
                    rental_data['renter']
                ))
                conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
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
            print(f"Database error: {e}")
            return []
    
    # === МЕТОДЫ ДЛЯ АВТОМОБИЛЕЙ ===
    
    def add_car(self, name: str, license_plate: str, purchase_price: float = 0) -> bool:
        """Добавление автомобиля"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO cars (name, license_plate, purchase_price, purchase_date)
                    VALUES (?, ?, ?, ?)
                ''', (name, license_plate, purchase_price, datetime.now()))
                conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
    
    def get_car(self, license_plate: str) -> Dict[str, Any]:
        """Получение автомобиля по номеру"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM cars WHERE license_plate = ?', (license_plate,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Database error: {e}")
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
            print(f"Database error: {e}")
            return []
    
    def update_car_status(self, license_plate: str, status: str) -> bool:
        """Обновление статуса автомобиля"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE cars SET status = ? WHERE license_plate = ?
                ''', (status, license_plate))
                conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
    
    def sell_car(self, license_plate: str, sale_price: float) -> bool:
        """Продажа автомобиля"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE cars SET status = 'sold', sale_price = ?, sale_date = ?
                    WHERE license_plate = ?
                ''', (sale_price, datetime.now(), license_plate))
                conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
    
    def delete_car(self, license_plate: str) -> bool:
        """Удаление автомобиля"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM cars WHERE license_plate = ?', (license_plate,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
    
    # === МЕТОДЫ ДЛЯ ОБСЛУЖИВАНИЯ ===
    
    def add_maintenance(self, car_id: int, amount: float, description: str) -> bool:
        """Добавление записи об обслуживании"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO maintenance (car_id, amount, description)
                    VALUES (?, ?, ?)
                ''', (car_id, amount, description))
                conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
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
            print(f"Database error: {e}")
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
            print(f"Database error: {e}")
            return []

# Глобальный экземпляр базы данных
db = Database()