import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import inspect, text

app = create_app()

# Auto-setup database tables for Vercel/Production
with app.app_context():
    try:
        # Create all tables if they don't exist
        db.create_all()
        print("✅ Database tables ensured")
        
        inspector = inspect(db.engine)
        user_columns = {column['name'] for column in inspector.get_columns('users')}

        with db.engine.connect() as conn:
            if 'is_approved' not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_approved BOOLEAN DEFAULT FALSE"))
            if db.engine.dialect.name == 'postgresql' and 'password_hash' in user_columns:
                conn.execute(text("ALTER TABLE users ALTER COLUMN password_hash TYPE VARCHAR(255)"))
            conn.execute(text("UPDATE users SET is_approved = TRUE WHERE is_approved IS NULL"))
            conn.commit()
            print("✅ Database schema patched")
    except Exception as e:
        print(f"⚠️ Database setup warning: {e}")

# WSGI application for Vercel
application = app
