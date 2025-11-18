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
            conn.commit()
    
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

# Глобальный экземпляр базы данных
db = Database()