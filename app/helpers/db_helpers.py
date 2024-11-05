from sqlalchemy import create_engine
import os

def db_connection():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_url = f"sqlite:///{os.path.join(base_dir, 'users.db')}"

    try:
        engine = create_engine(db_url)
        print ("Connection established")
        return engine
    except Exception as e:
        print(f"Error: '{e}'")
        print("Make sure you set up the database, "
              "and re-run this script.")
        return None

def create_table(engine):
    if engine is None:
        print("No connection available to create database.")
        return

    cursor = engine.cursor()
    try:
        cursor.execute(f"CREATE TABLE IF NOT EXISTS users "
                       f"(id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)")
    except Exception as err:
        print(f"Error: '{err}'")
    finally:
        cursor.close()
