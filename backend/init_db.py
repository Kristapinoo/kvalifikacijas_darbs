"""
Database initialization script
Run this to create all database tables
"""
from app import app
from extensions import db
import models

def init_database():
    """Create all database tables"""
    with app.app_context():
        # Drop all tables (only for development!)
        db.drop_all()

        # Create all tables
        db.create_all()

        print("✅ Database tables created successfully!")
        print("\nTables created:")
        print("  1. users")
        print("  2. tests")
        print("  3. study_materials")
        print("  4. assignments")
        print("  5. questions")
        print("  6. question_options")

if __name__ == '__main__':
    init_database()
