import sqlite3
from typing import Optional

DB_FILE = "accomodation.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def create_tables():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
              CREATE TABLE IF NOT EXISTS cities (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT UNIQUE
              )"""
            )
    

    c.execute("""
              CREATE TABLE IF NOT EXISTS attractions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT, 
              lat REAL,
              lon REAL,
              city_id INTEGER,
              FOREIGN KEY(city_id) REFERENCES cities(id))"""
            )
    

    c.execute("""
              CREATE TABLE IF NOT EXISTS accomodations (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT,
              lat REAL,
              lon REAL,
              price REAL,
              city_id INTEGER,
              FOREIGN KEY(city_id) REFERENCES cities(id))"""
            )
    
    conn.commit()
    conn.close()

def insert_city(name:str) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    # Insert or ignore duplicate
    cursor.execute("INSERT OR IGNORE INTO cities (name) VALUES (?)", (name,))
    conn.commit()

    # Always fetch ID (new or existing)
    cursor.execute("SELECT id FROM cities WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None
    
def insert_accomodation(name:str, lat:float, lon:float, price:float, city_id:int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO accomodations (name, lat, lon, price, city_id) VALUES (?, ?, ?, ?, ?)""", (name, lat, lon, price, city_id))
    conn.commit()
    conn.close()

def insert_attraction(name:str, lat:float, lon:float, city_id:int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO attractions (name, lat, lon, city_id) VALUES (?, ?, ?, ?)""", (name, lat, lon, city_id))
    conn.commit()
    conn.close()
