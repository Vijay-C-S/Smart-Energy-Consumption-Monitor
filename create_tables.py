"""Quick helper to create DB tables from SQLAlchemy models (dev only)."""
from app.database import engine, Base
import app.models

if __name__ == '__main__':
    print('Creating database tables...')
    Base.metadata.create_all(bind=engine)
    print('Done.')
