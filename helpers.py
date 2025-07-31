from fuzzywuzzy import fuzz

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
        "rice": ["brown rice", "quinoa", "jasmine rice"],
        "oil": ["vegetable oil", "olive oil", "canola oil"],
        "soy sauce": ["tamari", "coconut aminos", "liquid aminos"],
        "mozzarella": ["cheddar", "provolone", "vegan cheese"],
        "tomatoes": ["canned tomatoes", "sun-dried tomatoes", "red bell peppers"],
        "garlic": ["garlic powder", "shallots", "onion"],
        "ginger": ["ginger powder", "galangal", "turmeric"],
        "olive oil": ["canola oil", "vegetable oil", "avocado oil"],
        "canola oil": ["olive oil", "vegetable oil", "sunflower oil"],
        "vegetables": ["mixed vegetables", "frozen vegetables", "fresh vegetables"],
    }
    return substitutes.get(ingredient.lower(), ["No substitute available"])

def filter_by_restrictions(recipes, restrictions):
    if not restrictions:
        return recipes
    restr_list = [r.strip().lower() for r in restrictions.split(',') if r.strip()]
    if not restr_list:
        return recipes
    filtered = []
    for recipe in recipes:
        recipe_diets = [d.lower() for d in recipe.get("diets", [])]
        if any(restr in recipe_diets for restr in restr_list):
            filtered.append(recipe)
    return filtered