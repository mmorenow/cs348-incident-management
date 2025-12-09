import psycopg2
from psycopg2.extras import RealDictCursor
import os

def init_database():
    try:
        database_url = os.environ.get('DATABASE_URL')
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                id SERIAL PRIMARY KEY,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                date DATE NOT NULL,
                description TEXT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_incidents_date 
            ON incidents(date)
        ''')


        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_incidents_severity 
            ON incidents(severity)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_incidents_user_id 
            ON incidents(user_id)
        ''')

        cursor.execute('''
            INSERT INTO users (id, name, email, role)
            VALUES 
                (1, 'John Doe', 'john@example.com', 'Security Analyst'),
                (2, 'Marcelo Moreno', 'marcelo@example.com', 'CISO'),
                (3, 'Juan Carlos', 'juan@example.com', 'Security Engineer')
            ON CONFLICT (id) DO NOTHING
        ''')

        cursor.execute('''
            INSERT INTO incidents (id, type, severity, status, date, description, user_id)
            VALUES 
                (1, 'Phishing', 'High', 'Open', '2024-10-12', 'User clicked suspicious link', 1),
                (2, 'Malware', 'Critical', 'In Progress', '2024-10-15', 'Ransomware detected on workstation', 2),
                (3, 'Data Breach', 'High', 'Closed', '2024-10-10', 'Unauthorized access to database', NULL)
            ON CONFLICT (id) DO NOTHING
        ''')

        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully with tables and indexes!")

    except Exception as e:
        print(f"Error occurred: {e}")
        if conn:
            conn.rollback()
            cursor.close()
            conn.close()

if __name__ == '__main__':
    init_database()
