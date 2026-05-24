# db/operations.py
import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), 'user.db')

def init_db():
    """Initializes the SQLite database and creates both structured tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            goal_type TEXT,
            target_weight REAL
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weight_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,
            weight REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            UNIQUE(user_id, log_date)
        );
    ''')
    conn.commit()
    conn.close()

def get_user(user_id):
    """Fetches a user profile by their Telegram user ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, phone, goal_type, target_weight FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(user_id, name, phone=None):
    """Inserts a new user record upon their first /start command."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (user_id, name, phone) VALUES (?, ?, ?)", (user_id, name, phone))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def update_user_goal(user_id, goal_type, target_weight):
    """Updates the goal configuration details for an existing user profile."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET goal_type = ?, target_weight = ? WHERE user_id = ?", (goal_type, target_weight, user_id))
    conn.commit()
    conn.close()

def save_or_update_weight(user_id, weight):
    """Inserts or overwrites a daily weight log for today's date."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today_str = date.today().isoformat()
    try:
        cursor.execute('''
            INSERT INTO weight_logs (user_id, log_date, weight) VALUES (?, ?, ?)
            ON CONFLICT(user_id, log_date) DO UPDATE SET weight = excluded.weight;
        ''', (user_id, today_str, weight))
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"❌ [DB] Error logging weight: {e}")
    finally:
        conn.close()

def get_weight_bounds(user_id):
    """Fetches the first logged weight and the most recent logged weight."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT weight FROM weight_logs WHERE user_id = ? ORDER BY log_date ASC LIMIT 1", (user_id,))
    first_row = cursor.fetchone()
    cursor.execute("SELECT weight FROM weight_logs WHERE user_id = ? ORDER BY log_date DESC LIMIT 1", (user_id,))
    latest_row = cursor.fetchone()
    conn.close()
    return {
        "starting_weight": first_row[0] if first_row else None,
        "current_weight": latest_row[0] if latest_row else None
    }

def get_all_weight_logs(user_id):
    """Fetches all logged weights ordered chronologically."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT log_date, weight FROM weight_logs WHERE user_id = ? ORDER BY log_date ASC", (user_id,))
    logs = cursor.fetchall()
    conn.close()
    return logs

def has_logged_today(user_id):
    """Checks if a log exists for today's date."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today_str = date.today().isoformat()
    cursor.execute("SELECT 1 FROM weight_logs WHERE user_id = ? AND log_date = ?", (user_id, today_str))
    row = cursor.fetchone()
    conn.close()
    return row is not None

# 💡 NEW: Verification query to confirm line-item status
def check_log_exists_on_date(user_id, target_date):
    """Verifies if a weight log entry exists for a specific historical date string."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM weight_logs WHERE user_id = ? AND log_date = ?", (user_id, target_date))
    row = cursor.fetchone()
    conn.close()
    return row is not None

# 💡 NEW: Delete operation query
def delete_weight_log(user_id, target_date):
    """Removes a specific date log entry from the database tracking repository."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM weight_logs WHERE user_id = ? AND log_date = ?", (user_id, target_date))
    conn.commit()
    conn.close()

# 💡 NEW: Specific date modification query
def update_weight_on_date(user_id, target_date, new_weight):
    """Modifies the numerical target value for a specific historical date log row."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE weight_logs SET weight = ? WHERE user_id = ? AND log_date = ?", (new_weight, user_id, target_date))
    conn.commit()
    conn.close()