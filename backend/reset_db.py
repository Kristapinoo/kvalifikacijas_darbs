"""
Database reset script
WARNING: This will DROP ALL TABLES and DELETE ALL DATA!
Use this only when you want to completely reset the database.
For normal initialization, use init_db.py instead.
"""
from app import app
from extensions import db
import models

def reset_database():
    """Drop all tables and recreate them (deletes all data!)"""
    with app.app_context():
        print("WARNING: This will delete ALL data in the database!")
        response = input("Type 'yes' to confirm: ")

        if response.lower() != 'yes':
            print("Reset cancelled.")
            return

        print("\nDropping all tables...")
        db.drop_all()

        print("Creating new tables...")
        db.create_all()

        print("\nDatabase reset successfully!")
        print("\nTables created:")
        print("  1. users")
        print("  2. tests")
        print("  3. study_materials")
        print("  4. assignments")
        print("  5. questions")
        print("  6. question_options")

if __name__ == '__main__':
    reset_database()
