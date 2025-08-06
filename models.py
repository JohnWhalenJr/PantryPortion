from sqlalchemy import create_engine, Column, Integer, String, Float, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Set up the base for our database models
Base = declarative_base()
# Connect to a SQLite database called pantry.db
engine = create_engine('sqlite:///pantry.db', echo=False)

# Define the UserProfile table to store user info
class UserProfile(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)  # Unique ID for each user
    name = Column(String, unique=True)     # Username, must be unique
    password = Column(String)              # User’s password
    dietary_restrictions = Column(String, nullable=True)  # Optional dietary restrictions (e.g., "gluten-free")

# Define the Recipe table to store recipe data
class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)  # Unique ID for each recipe
    name = Column(String)                  # Recipe name
    ingredients = Column(String)           # Comma-separated list of ingredients
    instructions = Column(String)          # Cooking instructions
    calories = Column(Float)               # Calories per serving
    protein = Column(Float)                # Protein per serving
    fat = Column(Float)                    # Fat per serving
    carbs = Column(Float)                  # Carbs per serving

# Make sure the database has all the needed columns
def update_schema():
    inspector = inspect(engine)
    # Create the users table if it doesn’t exist
    if not inspector.has_table('users'):
        Base.metadata.tables['users'].create(engine)
    else:
        columns = [c['name'] for c in inspector.get_columns('users')]
        with engine.connect() as conn:
            # Add password column if missing
            if 'password' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN password TEXT"))
            # Add dietary_restrictions column if missing
            if 'dietary_restrictions' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN dietary_restrictions TEXT"))
    
    # Create the recipes table if it doesn’t exist
    if not inspector.has_table('recipes'):
        Base.metadata.tables['recipes'].create(engine)
    else:
        columns = [c['name'] for c in inspector.get_columns('recipes')]
        with engine.connect() as conn:
            # Add instructions column if missing
            if 'instructions' not in columns:
                conn.execute(text("ALTER TABLE recipes ADD COLUMN instructions TEXT"))

# Set up the database schema and create a session to interact with it
update_schema()
Session = sessionmaker(bind=engine)
session = Session()