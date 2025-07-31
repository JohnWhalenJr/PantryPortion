import requests
import logging
import re

# Setup logging
logging.basicConfig(filename='pantry_portion.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

# Conditional import for html2text
try:
    import html2text
except ImportError:
    html2text = None

# Spoonacular API key
API_KEY = "ff4b682cd1954372be0dfd48319e37e0"

# Function to clean HTML from instructions
def clean_instructions(instructions):
    if not instructions:
        return "No instructions available"
    if html2text:
        # Use html2text if available
        h = html2text.HTML2Text()
        h.body_only = True
        cleaned = h.handle(instructions)
        return cleaned.strip() or "No instructions available"
    else:
        # Fallback to regex if html2text is not installed
        cleaned = re.sub(r'<[^>]+>', '', instructions)  # Remove HTML tags
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()  # Normalize whitespace
        return cleaned or "No instructions available"

def fetch_recipes(ingredients):
    # Try original ingredients first
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={','.join(ingredients)}&number=30&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        logging.debug(f"API URL (original ingredients): {url}")
        if response.status_code == 200:
            recipes = response.json()
            logging.debug(f"API Response (original): {len(recipes)} recipes found - {recipes}")
            if recipes:
                return recipes
        else:
            logging.debug(f"API Error (original): Status code {response.status_code}, {response.text}")
        
        # Fallback to normalized ingredients
        normalized_ingredients = [i.lower().rstrip('s').replace(' ', '%20') for i in ingredients]
        url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={','.join(normalized_ingredients)}&number=30&apiKey={API_KEY}"
        response = requests.get(url)
        logging.debug(f"API URL (normalized ingredients): {url}")
        if response.status_code == 200:
            recipes = response.json()
            logging.debug(f"API Response (normalized): {len(recipes)} recipes found - {recipes}")
            if recipes:
                return recipes
        else:
            logging.debug(f"API Error (normalized): Status code {response.status_code}, {response.text}")
        
        # Fallback to broader terms
        broad_terms = {'rice': 'grain', 'lentils': 'legume', 'beans': 'legume', 'chicken': 'poultry'}
        broad_ingredients = [broad_terms.get(i.lower().rstrip('s'), i.lower().rstrip('s')) for i in ingredients]
        url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={','.join(broad_ingredients)}&number=30&apiKey={API_KEY}"
        response = requests.get(url)
        logging.debug(f"API URL (broad ingredients): {url}")
        if response.status_code == 200:
            recipes = response.json()
            logging.debug(f"API Response (broad): {len(recipes)} recipes found - {recipes}")
            return recipes
        else:
            logging.debug(f"API Error (broad): Status code {response.status_code}, {response.text}")
            return []
    except requests.RequestException as e:
        logging.debug(f"API Request Failed: {e}")
        return []

def fetch_random_recipes(restrictions):
    params = {'number': 15, 'apiKey': API_KEY}
    if restrictions:
        restr_list = [r.strip().lower().replace(' ', '-') for r in restrictions.split(',') if r.strip()]
        if restr_list:
            params['diet'] = ','.join(restr_list)
    url = "https://api.spoonacular.com/recipes/complexSearch"
    try:
        response = requests.get(url, params=params)
        logging.debug(f"API URL (complex search): {url}")
        if response.status_code == 200:
            recipes = response.json()['results']
            logging.debug(f"API Response (complex search): {len(recipes)} recipes found - {recipes}")
            return recipes
        else:
            logging.debug(f"API Error (complex search): Status code {response.status_code}, {response.text}")
            return []
    except requests.RequestException as e:
        logging.debug(f"API Request Failed (complex search): {e}")
        return []

def fetch_recipe_details(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=true&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            recipe = response.json()
            # Clean instructions
            recipe['instructions'] = clean_instructions(recipe.get('instructions'))
            return recipe
        else:
            logging.debug(f"Recipe Details Error: Status code {response.status_code}, {response.text}")
            return None
    except requests.RequestException as e:
        logging.debug(f"Recipe Details Request Failed: {e}")
        return None

def fetch_substitutes(ingredient):
    # Try original ingredient
    url = f"https://api.spoonacular.com/food/ingredients/substitutes?ingredientName={ingredient}&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        logging.debug(f"Substitutes URL (original): {url}")
        if response.status_code == 200:
            data = response.json()
            subs = data.get('substitutes', [])
            if subs:
                logging.debug(f"Substitutes found for {ingredient}: {subs}")
                return subs
            logging.debug(f"No substitutes found for {ingredient}")
        
        # Fallback to normalized ingredient
        normalized = ingredient.lower().rstrip('s').replace(' ', '%20')
        url = f"https://api.spoonacular.com/food/ingredients/substitutes?ingredientName={normalized}&apiKey={API_KEY}"
        response = requests.get(url)
        logging.debug(f"Substitutes URL (normalized): {url}")
        if response.status_code == 200:
            data = response.json()
            subs = data.get('substitutes', [])
            if subs:
                logging.debug(f"Substitutes found for {normalized}: {subs}")
                return subs
            logging.debug(f"No substitutes found for {normalized}")
        
        # Fallback to broader term
        broad_terms = {'rice': 'grain', 'lentils': 'legume', 'beans': 'legume', 'chicken': 'poultry', 'white rice': 'grain'}
        broad = broad_terms.get(normalized, normalized)
        url = f"https://api.spoonacular.com/food/ingredients/substitutes?ingredientName={broad}&apiKey={API_KEY}"
        response = requests.get(url)
        logging.debug(f"Substitutes URL (broad): {url}")
        if response.status_code == 200:
            data = response.json()
            subs = data.get('substitutes', [])
            if subs:
                logging.debug(f"Substitutes found for {broad}: {subs}")
                return subs
            logging.debug(f"No substitutes found for {broad}")
        
        # Fallback to synonym
        synonyms = {'rice': 'quinoa', 'lentils': 'chickpeas', 'beans': 'peas', 'chicken': 'turkey', 'white rice': 'brown rice'}
        synonym = synonyms.get(normalized, normalized)
        url = f"https://api.spoonacular.com/food/ingredients/substitutes?ingredientName={synonym}&apiKey={API_KEY}"
        response = requests.get(url)
        logging.debug(f"Substitutes URL (synonym): {url}")
        if response.status_code == 200:
            data = response.json()
            subs = data.get('substitutes', [])
            logging.debug(f"Substitutes found for {synonym}: {subs}")
            return subs if subs else ["No substitutes found for this ingredient"]
        else:
            logging.debug(f"Substitutes Error: {response.status_code}, {response.text}")
            return ["No substitutes available"]
    except requests.RequestException as e:
        logging.debug(f"Substitutes Request Failed: {e}")
        return ["No substitutes available"]

def fetch_similar_recipes(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/similar?number=5&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logging.debug(f"Similar Recipes Error: {response.status_code}, {response.text}")
            return []
    except requests.RequestException as e:
        logging.debug(f"Similar Recipes Request Failed: {e}")
        return []
