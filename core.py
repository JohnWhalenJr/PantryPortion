# core.py
from api import fetch_recipes, fetch_random_recipes
from helpers import suggest_substitution, filter_by_restrictions
from fuzzywuzzy import process
import logging

def get_filtered_recipes(ingredients, restrictions):
    common_ingredients = ['broccoli', 'lentils', 'rice', 'beans', 'chicken', 'tomatoes', 'garlic', 'olive oil']
    matched_ingredients = []
    for ingredient in ingredients:
        match = process.extractOne(ingredient.lower(), common_ingredients, score_cutoff=80)
        matched_ingredients.append(match[0] if match else ingredient.lower())
    
    logging.debug(f"Original Ingredients: {ingredients}, Matched: {matched_ingredients}")

    if matched_ingredients:
        recipes = fetch_recipes(matched_ingredients, restrictions)
        filtered_recipes = filter_by_restrictions(recipes, restrictions)
        return filtered_recipes if filtered_recipes else recipes
    else:
        return fetch_random_recipes(restrictions)
