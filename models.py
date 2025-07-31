from sqlalchemy import create_engine, Column, Integer, String, Float, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///pantry.db', echo=False)

class UserProfile(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    password = Column(String)
    dietary_restrictions = Column(String, nullable=True)

class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    ingredients = Column(String)
    instructions = Column(String)
    calories = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    carbs = Column(Float)

def update_schema():
    inspector = inspect(engine)
    if not inspector.has_table('users'):
        Base.metadata.tables['users'].create(engine)
    else:
        columns = [c['name'] for c in inspector.get_columns('users')]
        with engine.connect() as conn:
            if 'password' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN password TEXT"))
            if 'dietary_restrictions' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN dietary_restrictions TEXT"))
    
    if not inspector.has_table('recipes'):
        Base.metadata.tables['recipes'].create(engine)
    else:
        columns = [c['name'] for c in inspector.get_columns('recipes')]
        with engine.connect() as conn:
            if 'instructions' not in columns:
                conn.execute(text("ALTER TABLE recipes ADD COLUMN instructions TEXT"))

# Update schema and create session
update_schema()
Session = sessionmaker(bind=engine)
session = Session()
