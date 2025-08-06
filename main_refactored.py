# main_refactored.py

import csv
import logging
from models import UserProfile, Recipe, session
from api import fetch_recipes, fetch_random_recipes, fetch_recipe_details, fetch_substitutes, fetch_similar_recipes
from helpers import suggest_substitution, filter_by_restrictions
from fuzzywuzzy import process

logging.basicConfig(filename='pantry_portion.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

# ========== User Authentication ==========

def create_account(username, password, restrictions=None):
    existing_user = session.query(UserProfile).filter_by(name=username).first()
    if existing_user:
        return False, "Username already exists."
    
    user = UserProfile(name=username, password=password, dietary_restrictions=restrictions)
    session.add(user)
    try:
        session.commit()
        with open('users.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username, password, restrictions or ''])
        return True, user
    except Exception as e:
        session.rollback()
        return False, f"Error creating account: {e}"

def login(username, password):
    user = session.query(UserProfile).filter_by(name=username, password=password).first()
    if user:
        return True, user
    return False, "Invalid credentials"

# ========== Recipe Handling ==========

def fuzzy_match_ingredients(ingredients):
    common_ingredients = [
        'broccoli', 'lentils', 'rice', 'beans', 'chicken',
        'tomatoes', 'garlic', 'olive oil', 'onions', 'beef',
        'carrots', 'celery', 'eggs', 'fish', 'turkey', 'butter',
        'cheddar cheese', 'milk', 'parmesan', 'yogurt'
    ]
    matched = []
    for ingredient in ingredients:
        # Direct match if in list
        if ingredient.lower() in common_ingredients:
            matched.append(ingredient.lower())
        else:
            match = process.extractOne(ingredient.lower(), common_ingredients, score_cutoff=80)
            matched.append(match[0] if match else ingredient.lower())
    return matched


def get_filtered_recipes(ingredients, restrictions):
    if ingredients:
        matched = fuzzy_match_ingredients(ingredients)
        # Convert restrictions list to string if not None
        restr_str = None
        if restrictions:
            if isinstance(restrictions, list):
                restr_str = ",".join(restrictions)
            else:
                restr_str = restrictions
        recipes = fetch_recipes(matched, restr_str)
        filtered = filter_by_restrictions(recipes, restrictions)
        if not filtered and recipes:
            return recipes, "No recipes matched restrictions. Showing all recipes instead."
        return filtered, ""
    else:
        restr_str = None
        if restrictions:
            if isinstance(restrictions, list):
                restr_str = ",".join(restrictions)
            else:
                restr_str = restrictions
        return fetch_random_recipes(restr_str), ""


def get_recipe_details_by_id(recipe_id):
    details = fetch_recipe_details(recipe_id)
    if not details:
        return None

    nutrients = {n['name']: n['amount'] for n in details.get('nutrition', {}).get('nutrients', [])}
    
    recipe = Recipe(
        name=details['title'],
        ingredients=",".join([i['name'] for i in details.get('extendedIngredients', [])]),
        instructions=details.get('instructions', 'No instructions available'),
        calories=nutrients.get('Calories', 0),
        protein=nutrients.get('Protein', 0),
        fat=nutrients.get('Fat', 0),
        carbs=nutrients.get('Carbohydrates', 0)
    )
    session.add(recipe)
    session.commit()
    return details

def get_substitutes_for_ingredients(ingredients):
    return {ingredient: suggest_substitution(ingredient) for ingredient in ingredients}

def get_similar_recipes(recipe_id, limit=3):
    return fetch_similar_recipes(recipe_id)[:limit]
