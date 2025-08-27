#!/usr/bin/env python3
"""
Initialize PostgreSQL database tables for Resume Doctor AI
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def init_database():
    """Initialize all database tables"""
    print("🗄️ Initializing PostgreSQL database tables...")

    try:
        # Import after path is set
        from app_fixed import create_app

        # Create the Flask app
        app = create_app()

        with app.app_context():
            print("🔗 Connected to PostgreSQL database")

            # Import db within app context
            from models import db

            # Check current tables
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"📋 Existing tables: {existing_tables}")

            if existing_tables:
                print("🧹 Dropping existing tables for clean setup...")
                db.drop_all()

            # Create all tables
            print("🏗️ Creating all tables...")
            db.create_all()

            # Verify tables were created
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            print("✅ Database tables created successfully!")
            print(f"📋 Created tables: {', '.join(tables)}")

            # Test database connection
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.fetchone():
                    print("🔗 Database connection test: ✅ PASSED")

            return True

    except ImportError as e:
        print(f"❌ Import error (SQLAlchemy compatibility issue): {e}")
        print("💡 Try: pip install --upgrade SQLAlchemy Flask-SQLAlchemy")
        return False
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = init_database()
    if success:
        print("\n🎉 PostgreSQL database is ready! You can now run the application.")
        print("🚀 Run: python app_fixed.py")
    else:
        print("\n❌ Database initialization failed. Check the errors above.")
        print("💡 Make sure PostgreSQL is running and accessible.")
