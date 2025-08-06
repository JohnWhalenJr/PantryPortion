from api import fetch_substitutes
import logging

# Get substitute ingredients by calling the API
def suggest_substitution(ingredient):
    # Just pass the ingredient to the API function and return what it gives us
    return fetch_substitutes(ingredient)

# Filter recipes to match the user’s dietary restrictions
def filter_by_restrictions(recipes, restrictions):
    # If there are no restrictions, keep all recipes
    if not restrictions:
        return recipes
    # Clean up restrictions (e.g., "gluten free" becomes "gluten-free" to match the API)
    restr_list = [r.strip().lower().replace(' ', '-') for r in restrictions.split(',') if r.strip()]
    if not restr_list:
        return recipes
    filtered = []
    for recipe in recipes:
        # Get the diet tags for this recipe and clean them up
        recipe_diets = [d.lower().replace(' ', '-') for d in recipe.get("diets", [])]
        logging.debug(f"Recipe: {recipe.get('title', 'Unknown')}, Diets: {recipe_diets}, Required: {restr_list}")
        # Keep the recipe if it matches any restriction or is gluten-free compatible
        if any(restr in recipe_diets for restr in restr_list):
            filtered.append(recipe)
        elif 'gluten-free' in restr_list:
            # Check ingredients for gluten-containing items
            ingredients = [i['name'].lower() for i in recipe.get('usedIngredients', []) + recipe.get('missedIngredients', [])]
            gluten_items = ['wheat', 'barley', 'rye', 'flour', 'bread', 'pasta']
            if not any(g in i for i in ingredients for g in gluten_items):
                filtered.append(recipe)
                logging.debug(f"Added {recipe.get('title', 'Unknown')} as gluten-free compatible (no gluten ingredients)")
    logging.debug(f"Filtered {len(filtered)} recipes from {len(recipes)} for restrictions: {restr_list}")
    return filtered