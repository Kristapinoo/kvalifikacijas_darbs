"""
Database initialization script
Creates database tables ONLY if they don't exist yet.
Use reset_db.py to drop existing tables and recreate.
"""
from app import app
from extensions import db
import models
from sqlalchemy import inspect

def init_database():
    """Create database tables if they don't exist"""
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        if existing_tables:
            print("Database tables already exist:")
            for table in existing_tables:
                print(f"  - {table}")
            print("\nUse 'npm run reset-db' to drop and recreate tables")
            return

        db.create_all()

        print("Database tables created successfully!")
        print("\nTables created:")
        print("  1. users")
        print("  2. tests")
        print("  3. study_materials")
        print("  4. assignments")
        print("  5. questions")
        print("  6. question_options")

if __name__ == '__main__':
    init_database()
