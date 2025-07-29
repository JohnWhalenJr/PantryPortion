
import requests
from fuzzywuzzy import fuzz
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine('sqlite:///pantry.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# User profile model
class UserProfile(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    dietary_restrictions = Column(String)

# Recipe model
class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    ingredients = Column(String)
    instructions = Column(String)  # Added for recipe instructions
    calories = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    carbs = Column(Float)

Base.metadata.create_all(engine)

# Spoonacular API key
API_KEY = "ff4b682cd1954372be0dfd48319e37e0"

# Fetch recipes from Spoonacular
def fetch_recipes(ingredients):
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={','.join(ingredients)}&number=5&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            recipes = response.json()
            print(f"API Response: {len(recipes)} recipes found")
            return recipes
        else:
            print(f"API Error: Status code {response.status_code}, {response.text}")
            return []
    except requests.RequestException as e:
        print(f"API Request Failed: {e}")
        return []

# Fetch detailed recipe information
def fetch_recipe_details(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=true&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Recipe Details Error: Status code {response.status_code}, {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Recipe Details Request Failed: {e}")
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
    }
    return substitutes.get(ingredient.lower(), ["No substitute available"])

# Filter recipes by dietary restrictions
def filter_by_restrictions(recipes, restrictions):
    filtered = []
    for recipe in recipes:
        if not restrictions or "vegetarian" in restrictions.lower() and "vegetarian" in recipe.get("diets", []):
            filtered.append(recipe)
    print(f"Filtered Recipes: {len(filtered)} after applying restrictions")
    return filtered

# CLI interface
def main():
    print("Welcome to PantryPortion!")
    
    # Get user input
    name = input("Enter your name: ")
    ingredients = input("Enter ingredients (comma-separated): ").split(",")
    ingredients = [i.strip() for i in ingredients]
    restrictions = input("Enter dietary restrictions (e.g., vegetarian, or leave blank): ")
    
    # Save user profile
    session.add(UserProfile(name=name, dietary_restrictions=restrictions))
    session.commit()
    print("Profile saved!")
    
    # Fuzzy match ingredients
    available_ingredients = [
        "milk", "butter", "egg", "flour", "sugar", "ground turkey", "peanut oil",
        "cooking oil", "mixed vegetables", "pork dumplings", "chicken", "beef", "rice", "pasta", "spices"
    ]
    matched_ingredients = []
    for ingredient in ingredients:
        best_match = max(available_ingredients, key=lambda x: fuzz.ratio(ingredient.lower(), x))
        score = fuzz.ratio(ingredient.lower(), best_match)
        print(f"Matching '{ingredient}' to '{best_match}' (score: {score})")
        if score > 60:  # Further lowered threshold for better matching
            matched_ingredients.append(best_match)
    
    print(f"Matched Ingredients: {matched_ingredients}")
    
    # Fetch and filter recipes
    recipes = fetch_recipes(matched_ingredients)
    filtered_recipes = filter_by_restrictions(recipes, restrictions)
    
    # Display recipes
    print("\nAvailable Recipes:")
    if filtered_recipes:
        for i, recipe in enumerate(filtered_recipes, 1):
            print(f"{i}. {recipe['title']}")
    else:
        print("No recipes found. Try different ingredients or check API key.")
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
                    # Store in database
                    session.add(Recipe(
                        name=details['title'],
                        ingredients=",".join([i['name'] for i in details.get('extendedIngredients', [])]),
                        instructions=details.get('instructions', 'No instructions available'),
                        calories=details.get('nutrition', {}).get('nutrients', [{}])[0].get('amount', 0),
                        protein=details.get('nutrition', {}).get('nutrients', [{}])[1].get('amount', 0) if len(details.get('nutrition', {}).get('nutrients', [])) > 1 else 0,
                        fat=details.get('nutrition', {}).get('nutrients', [{}])[2].get('amount', 0) if len(details.get('nutrition', {}).get('nutrients', [])) > 2 else 0,
                        carbs=details.get('nutrition', {}).get('nutrients', [{}])[3].get('amount', 0) if len(details.get('nutrition', {}).get('nutrients', [])) > 3 else 0
                    ))
                    session.commit()
                    
                    # Display details
                    print(f"\nRecipe: {details['title']}")
                    print("Ingredients:")
                    for ing in details.get('extendedIngredients', []):
                        print(f"- {ing['original']}")
                    print("\nInstructions:")
                    print(details.get('instructions', 'No instructions available') or 'No instructions available')
                    print("\nNutritional Info:")
                    print(f"Calories: {details.get('nutrition', {}).get('nutrients', [{}])[0].get('amount', 0)}")
                    print(f"Protein: {details.get('nutrition', {}).get('nutrients', [{}])[1].get('amount', 0) if len(details.get('nutrition', {}).get('nutrients', [])) > 1 else 0}")
                    print(f"Fat: {details.get('nutrition', {}).get('nutrients', [{}])[2].get('amount', 0) if len(details.get('nutrition', {}).get('nutrients', [])) > 2 else 0}")
                    print(f"Carbs: {details.get('nutrition', {}).get('nutrients', [{}])[3].get('amount', 0) if len(details.get('nutrition', {}).get('nutrients', [])) > 3 else 0}")
                else:
                    print("Failed to fetch recipe details.")
            else:
                print(f"Please enter a number between 1 and {len(filtered_recipes)}.")
        except ValueError:
            print("Invalid input. Enter a number or 'q' to quit.")
    
    # Show substitutions
    print("\nIngredient Substitutions:")
    for ingredient in ingredients:
        subs = suggest_substitution(ingredient)
        print(f"{ingredient}: {subs}")

if __name__ == "__main__":
    main()
