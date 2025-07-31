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
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={','.join(ingredients)}&number=15&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        logging.debug(f"API URL (ingredients): {url}")
        if response.status_code == 200:
            recipes = response.json()
            logging.debug(f"API Response (ingredients): {len(recipes)} recipes found - {recipes}")
            return recipes
        else:
            logging.debug(f"API Error (ingredients): Status code {response.status_code}, {response.text}")
            return []
    except requests.RequestException as e:
        logging.debug(f"API Request Failed (ingredients): {e}")
        return []

def fetch_random_recipes(restrictions):
    params = {'number': 15, 'apiKey': API_KEY}
    if restrictions:
        restr_list = [r.strip().lower() for r in restrictions.split(',') if r.strip()]
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
