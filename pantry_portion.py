import requests
from fuzzywuzzy import fuzz
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
import csv

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine('sqlite:///pantry.db', echo=False)

# User profile model
class UserProfile(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    password = Column(String)
    dietary_restrictions = Column(String, nullable=True)

# Recipe model
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

# Function to update schema if needed
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

# Update schema
update_schema()

# Session setup
Session = sessionmaker(bind=engine)
session = Session()

# Spoonacular API key
API_KEY = "ff4b682cd1954372be0dfd48319e37e0"

# Fetch recipes from Spoonacular
def fetch_recipes(ingredients):
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={','.join(ingredients)}&number=5&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except requests.RequestException:
        return []

# Fetch detailed recipe information
def fetch_recipe_details(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=true&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException:
        return None

# Suggest ingredient substitutions
def suggest_substitution(ingredient):
    substitutes = {
        "milk": ["almond milk", "soy milk", "oat milk"],
        "butter": ["margarine", "olive oil", "coconut oil"],
        "egg": ["flaxseed", "applesauce", "tofu"],
        "ground turkey": ["ground chicken", "ground beef", "tofu"],
        "peanut oil": ["vegetable oil", "canola oil", "sesame oil"],
        "cooking oil": ["vegetable oil", "canola oil", "olive oil"],
        "mixed vegetables": ["frozen vegetables", "fresh vegetables"],
        "pork dumplings": ["chicken dumplings", "vegetable dumplings"],
        "chicken": ["turkey", "tofu", "pork"],
        "spices": ["herbs", "seasoning blend"],
        "white rice": ["brown rice", "quinoa", "jasmine rice"],
        "oil": ["vegetable oil", "olive oil", "canola oil"],
        "soy sauce": ["tamari", "coconut aminos", "liquid aminos"],
    }
    return substitutes.get(ingredient.lower(), ["No substitute available"])

# Filter recipes by dietary restrictions
def filter_by_restrictions(recipes, restrictions):
    if not restrictions:
        return recipes
    restr_list = [r.strip().lower() for r in restrictions.split(',') if r.strip()]
    if not restr_list:
        return recipes
    filtered = []
    for recipe in recipes:
        recipe_diets = [d.lower() for d in recipe.get("diets", [])]
        if all(restr in recipe_diets for restr in restr_list):
            filtered.append(recipe)
    return filtered

# CLI interface
def main():
    print("\n=== Welcome to PantryPortion! ===")
    
    action = input("Login (l) or Create account (c)? ").lower()
    if action == 'c':
        name = input("Enter username: ")
        password = input("Enter password: ")
        restrictions = input("Enter dietary restrictions (comma-separated, e.g., vegetarian,vegan,gluten-free, or leave blank): ") or None
        user = UserProfile(name=name, password=password, dietary_restrictions=restrictions)
        session.add(user)
        try:
            session.commit()
            with open('users.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([name, password, restrictions or ''])
            print("Account created!")
        except Exception as e:
            print(f"Error creating account: {e}")
            session.rollback()
            return
    elif action == 'l':
        name = input("Enter username: ")
        password = input("Enter password: ")
        user = session.query(UserProfile).filter_by(name=name, password=password).first()
        if user:
            print("Login successful!")
            restrictions = user.dietary_restrictions
        else:
            print("Invalid credentials.")
            return
    else:
        print("Invalid choice.")
        return
    
    ingredients = input("\nEnter ingredients (comma-separated): ").split(",")
    ingredients = [i.strip() for i in ingredients]
    
    # Fuzzy match ingredients
    available_ingredients = [
        "milk", "butter", "egg", "flour", "sugar", "ground turkey", "peanut oil",
        "cooking oil", "mixed vegetables", "pork dumplings", "chicken", "beef",
        "white rice", "rice", "pasta", "spices", "oil", "soy sauce"
    ]
    matched_ingredients = []
    for ingredient in ingredients:
        best_match = max(available_ingredients, key=lambda x: fuzz.ratio(ingredient.lower(), x))
        score = fuzz.ratio(ingredient.lower(), best_match)
        if score >= 80:
            matched_ingredients.append(best_match)
    
    # Fetch and filter recipes
    recipes = fetch_recipes(matched_ingredients)
    filtered_recipes = filter_by_restrictions(recipes, restrictions)
    
    # Display recipes
    print("\n=== Available Recipes ===")
    if filtered_recipes:
        for i, recipe in enumerate(filtered_recipes, 1):
            print(f"{i} {recipe['title']}")
    else:
        print("No recipes found. Try different ingredients.")
        print("\n=== Ingredient Substitutions ===")
        for ingredient in ingredients:
            subs = suggest_substitution(ingredient)
            print(f"{ingredient}: {subs}")
        return
    
    # Allow user to select a recipe
    while True:
        try:
            choice = input("\nEnter the number of the recipe to view details (or 'q' to quit): ")
            if choice.lower() == 'q':
                break
            choice = int(choice)
            if 1 <= choice <= len(filtered_recipes):
                selected_recipe = filtered_recipes[choice - 1]
                details = fetch_recipe_details(selected_recipe['id'])
                if details:
                    nutrients = {n['name']: n['amount'] for n in details.get('nutrition', {}).get('nutrients', [])}
                    # Store in database
                    session.add(Recipe(
                        name=details['title'],
                        ingredients=",".join([i['name'] for i in details.get('extendedIngredients', [])]),
                        instructions=details.get('instructions', 'No instructions available'),
                        calories=nutrients.get('Calories', 0),
                        protein=nutrients.get('Protein', 0),
                        fat=nutrients.get('Fat', 0),
                        carbs=nutrients.get('Carbohydrates', 0)
                    ))
                    session.commit()
                    
                    # Display details
                    print(f"\n=== Recipe: {details['title']} ===")
                    print("Ingredients:")
                    for ing in details.get('extendedIngredients', []):
                        print(f"- {ing['original']}")
                    print("\nInstructions:")
                    instructions = details.get('instructions', 'No instructions available') or 'No instructions available'
                    print(instructions)
                    if "white rice" in matched_ingredients:
                        print("**brown rice variation: Follow the instructions for the white rice version, substituting an equal amount of brown basmati rice for the white (I find you don't really need to rinse brown rice). Increase the water to 3c. and increase the cook time to 40-50 minutes.")
                    print("\nNutritional Info:")
                    print(f"Calories: {nutrients.get('Calories', 0)}")
                    print(f"Protein: {nutrients.get('Protein', 0)}")
                    print(f"Fat: {nutrients.get('Fat', 0)}")
                    print(f"Carbs: {nutrients.get('Carbohydrates', 0)}")
                    print("\n=== Ingredient Substitutions ===")
                    for ingredient in ingredients:
                        subs = suggest_substitution(ingredient)
                        print(f"{ingredient}: {subs}")
                else:
                    print("Failed to fetch recipe details.")
            else:
                print(f"Please enter a number between 1 and {len(filtered_recipes)}.")
        except ValueError:
            print("Invalid input. Enter a number or 'q' to quit.")

if __name__ == "__main__":
    main()
