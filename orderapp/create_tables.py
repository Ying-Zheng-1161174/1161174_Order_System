import sys
import os
from sqlalchemy import create_engine
from orderapp import db
from orderapp.config import Config

# Set up path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

def create_all_tables():
    # Create engine using the configuration
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    # Create all tables
    db.metadata.create_all(engine)

if __name__ == "__main__":
    create_all_tables()
    print("Tables created successfully.")

