"""
Database setup script - creates all tables in Neon Postgres
Run this after setting up your DATABASE_URL in .env
"""
from database import engine, Base
from models import User, UserProfile, PersonalizationCache, ChatHistory
import sys
import cohere

def create_tables():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] All tables created successfully!")
        print("\nCreated tables:")
        print("  - users")
        print("  - user_profiles")
        print("  - personalization_cache")
        print("  - chat_history")
        print("\nDatabase is ready to use!")
        return True
    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def drop_tables():
    """Drop all tables (use with caution!)"""
    response = input("[WARNING] This will delete ALL data. Are you sure? (yes/no): ")
    if response.lower() == "yes":
        try:
            print("Dropping all tables...")
            Base.metadata.drop_all(bind=engine)
            print("[SUCCESS] All tables dropped successfully!")
            return True
        except Exception as e:
            print(f"[ERROR] Error dropping tables: {e}")
            return False
    else:
        print("Operation cancelled.")
        return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Database setup for Physical AI Book")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all tables before creating (WARNING: deletes all data)"
    )

    args = parser.parse_args()

    if args.drop:
        if drop_tables():
            create_tables()
    else:
        create_tables()
