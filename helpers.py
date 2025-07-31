from api import fetch_substitutes
import logging

def suggest_substitution(ingredient):
    return fetch_substitutes(ingredient)

def filter_by_restrictions(recipes, restrictions):
    if not restrictions:
        return recipes
    restr_list = [r.strip().lower().replace(' ', '-') for r in restrictions.split(',') if r.strip()]  # Normalize, e.g., "gluten free" -> "gluten-free"
    if not restr_list:
        return recipes
    filtered = []
    for recipe in recipes:
        recipe_diets = [d.lower().replace(' ', '-') for d in recipe.get("diets", [])]  # Normalize API diet tags
        logging.debug(f"Recipe: {recipe.get('title', 'Unknown')}, Diets: {recipe_diets}, Required: {restr_list}")
        if any(restr in recipe_diets for restr in restr_list):  # Allow any restriction to match
            filtered.append(recipe)
    logging.debug(f"Filtered {len(filtered)} recipes from {len(recipes)} for restrictions: {restr_list}")
    return filtered
