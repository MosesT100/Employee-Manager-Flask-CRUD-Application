# database.py (updated)
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE = os.getenv('DATABASE_NAME', 'crud_app.db')

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the employees table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL,
            salary REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed sample data if enabled and table is empty
    seed_data = os.getenv('SEED_SAMPLE_DATA', 'True').lower() == 'true'

    if seed_data:
        cursor.execute('SELECT COUNT(*) FROM employees')
        count = cursor.fetchone()[0]

        if count == 0:
            sample_data = [
                ('Alice Johnson', 'alice@example.com', 'Engineering', 85000),
                ('Bob Smith', 'bob@example.com', 'Marketing', 72000),
                ('Carol Williams', 'carol@example.com', 'HR', 68000),
            ]
            cursor.executemany(
                'INSERT INTO employees (name, email, department, salary) '
                'VALUES (?, ?, ?, ?)',
                sample_data
            )
            print("✅ Sample data inserted.")

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")