import requests
import logging
import re

# Set up logging to save debug info to a file called pantry_portion.log, so we can track what's happening
logging.basicConfig(filename='pantry_portion.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

# Try to bring in html2text to handle HTML content; if it’s not installed, we’ll work around it
try:
    import html2text
except ImportError:
    html2text = None

# Our Spoonacular API key, which lets us talk to their recipe database
API_KEY = "ff4b682cd1954372be0dfd48319e37e0"
# API_KEY = "d561d123d5d44aaa8d705d54baafd587"


# Clean up recipe instructions by removing HTML tags to make them readable
def clean_instructions(instructions):
    # If there are no instructions, just say so
    if not instructions:
        return "No instructions available"
    if html2text:
        # If we have html2text, use it to strip HTML and keep just the plain text
        h = html2text.HTML2Text()
        h.body_only = True
        cleaned = h.handle(instructions)
        return cleaned.strip() or "No instructions available"
    else:
        # If html2text isn’t available, use regex to remove HTML tags and clean up extra spaces
        cleaned = re.sub(r'<[^>]+>', '', instructions)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned or "No instructions available"

# Find recipes that match the user’s ingredients using the Spoonacular API
def fetch_recipes(ingredients, restrictions=None):
    # Base parameters for the API call
    params = {'ingredients': ','.join(ingredients), 'number': 30, 'apiKey': API_KEY}
    # Add gluten-free intolerance if specified in restrictions
    if restrictions and 'gluten-free' in [r.strip().lower().replace(' ', '-') for r in restrictions if r.strip()]:
        params['intolerances'] = 'gluten'
    
    # Try original ingredients first
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    try:
        response = requests.get(url, params=params)
        logging.debug(f"API URL (original ingredients): {url}?{requests.compat.urlencode(params)}")
        if response.status_code == 200:
            recipes = response.json()
            logging.debug(f"API Response (original): {len(recipes)} recipes found - {recipes}")
            if recipes:
                return recipes
        else:
            logging.debug(f"API Error (original): Status code {response.status_code}, {response.text}")
        
        # Try pluralized ingredients (e.g., "lentil" -> "lentils")
        plural_ingredients = [i.lower() + 's' if not i.lower().endswith('s') else i.lower() for i in ingredients]
        params['ingredients'] = ','.join(plural_ingredients)
        response = requests.get(url, params=params)
        logging.debug(f"API URL (plural ingredients): {url}?{requests.compat.urlencode(params)}")
        if response.status_code == 200:
            recipes = response.json()
            logging.debug(f"API Response (plural): {len(recipes)} recipes found - {recipes}")
            if recipes:
                return recipes
        else:
            logging.debug(f"API Error (plural): Status code {response.status_code}, {response.text}")
        
        # Fallback to normalized ingredients (lowercase, remove ‘s’, encode spaces)
        normalized_ingredients = [i.lower().rstrip('s').replace(' ', '%20') for i in ingredients]
        params['ingredients'] = ','.join(normalized_ingredients)
        response = requests.get(url, params=params)
        logging.debug(f"API URL (normalized ingredients): {url}?{requests.compat.urlencode(params)}")
        if response.status_code == 200:
            recipes = response.json()
            logging.debug(f"API Response (normalized): {len(recipes)} recipes found - {recipes}")
            if recipes:
                return recipes
        else:
            logging.debug(f"API Error (normalized): Status code {response.status_code}, {response.text}")
        
        # Last try: use broader terms like ‘grain’ for ‘rice’ to increase chances of finding recipes
        broad_terms = {'rice': 'grain', 'lentils': 'legume', 'beans': 'legume', 'chicken': 'poultry', 'broccoli': 'vegetable'}
        broad_ingredients = [broad_terms.get(i.lower().rstrip('s'), i.lower().rstrip('s')) for i in ingredients]
        params['ingredients'] = ','.join(broad_ingredients)
        response = requests.get(url, params=params)
        logging.debug(f"API URL (broad ingredients): {url}?{requests.compat.urlencode(params)}")
        if response.status_code == 200:
            recipes = response.json()
            logging.debug(f"API Response (broad): {len(recipes)} recipes found - {recipes}")
            return recipes
        else:
            logging.debug(f"API Error (broad): Status code {response.status_code}, {response.text}")
            return []
    except requests.RequestException as e:
        # Log any network or request errors and return nothing
        logging.debug(f"API Request Failed: {e}")
        return []

# Get random recipes, optionally filtered by dietary restrictions
def fetch_random_recipes(restrictions):
    params = {'number': 15, 'apiKey': API_KEY}
    if restrictions:
        # Clean up restrictions (e.g., turn "gluten free" into "gluten-free" for the API)
        restr_list = [r.strip().lower().replace(' ', '-') for r in restrictions.split(',') if r.strip()]
        if restr_list:
            params['diet'] = ','.join(restr_list)
            if 'gluten-free' in restr_list:
                params['intolerances'] = 'gluten'  # Add gluten intolerance for stricter filtering
    url = "https://api.spoonacular.com/recipes/complexSearch"
    try:
        response = requests.get(url, params=params)
        logging.debug(f"API URL (complex search): {url}?{requests.compat.urlencode(params)}")
        if response.status_code == 200:
            recipes = response.json()['results']
            logging.debug(f"API Response (complex search): {len(recipes)} recipes found - {recipes}")
            if recipes:
                return recipes
        else:
            logging.debug(f"API Error (complex search): Status code {response.status_code}, {response.text}")
        
        # Fallback: try without diet restrictions if no results
        if restrictions:
            params.pop('diet', None)
            params.pop('intolerances', None)
            response = requests.get(url, params=params)
            logging.debug(f"API URL (fallback, no restrictions): {url}?{requests.compat.urlencode(params)}")
            if response.status_code == 200:
                recipes = response.json()['results']
                logging.debug(f"API Response (fallback): {len(recipes)} recipes found - {recipes}")
                return recipes
            else:
                logging.debug(f"API Error (fallback): Status code {response.status_code}, {response.text}")
        return []
    except requests.RequestException as e:
        # Log any errors and return an empty list
        logging.debug(f"API Request Failed (complex search): {e}")
        return []

# Get detailed info for a specific recipe, like ingredients and nutrition
def fetch_recipe_details(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=true&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            recipe = response.json()
            # Clean up the instructions to remove any HTML
            recipe['instructions'] = clean_instructions(recipe.get('instructions'))
            return recipe
        else:
            logging.debug(f"Recipe Details Error: Status code {response.status_code}, {response.text}")
            return None
    except requests.RequestException as e:
        # Log any errors and return None
        logging.debug(f"Recipe Details Request Failed: {e}")
        return None

# Find substitute ingredients for a given ingredient using the Spoonacular API
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
        
        # Try corrected ingredient (e.g., "broccoli" -> "broccoli")
        common_ingredients = ['broccoli', 'lentils', 'rice', 'beans', 'chicken', 'tomatoes', 'garlic', 'olive oil']
        from fuzzywuzzy import process
        match = process.extractOne(ingredient.lower(), common_ingredients, score_cutoff=80)
        corrected = match[0] if match else ingredient.lower()
        url = f"https://api.spoonacular.com/food/ingredients/substitutes?ingredientName={corrected}&apiKey={API_KEY}"
        response = requests.get(url)
        logging.debug(f"Substitutes URL (corrected): {url}")
        if response.status_code == 200:
            data = response.json()
            subs = data.get('substitutes', [])
            if subs:
                logging.debug(f"Substitutes found for {corrected}: {subs}")
                return subs
            logging.debug(f"No substitutes found for {corrected}")
        
        # Try pluralized ingredient
        plural = corrected + 's' if not corrected.endswith('s') else corrected
        url = f"https://api.spoonacular.com/food/ingredients/substitutes?ingredientName={plural}&apiKey={API_KEY}"
        response = requests.get(url)
        logging.debug(f"Substitutes URL (plural): {url}")
        if response.status_code == 200:
            data = response.json()
            subs = data.get('substitutes', [])
            if subs:
                logging.debug(f"Substitutes found for {plural}: {subs}")
                return subs
            logging.debug(f"No substitutes found for {plural}")
        
        # Fallback to normalized ingredient (lowercase, remove 's', URL-encode spaces)
        normalized = corrected.rstrip('s').replace(' ', '%20')
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
        broad_terms = {'rice': 'grain', 'lentils': 'legume', 'beans': 'legume', 'chicken': 'poultry', 'white rice': 'grain', 'broccoli': 'vegetable'}
        broad = broad_terms.get(normalized, normalized)
        url = f"https://api.spoonacular.com/food/ingredients/substitutes?ingredientName={broad}&apiKey={API_KEY}"
        response = requests.get(url)
        logging.debug(f"Substitutes URL (broad): {url}")
        if response.status_code == 200:
            data = response.json()
            subs = data.get('substitutes', [])
            logging.debug(f"Substitutes found for {broad}: {subs}")
            return subs if subs else ["No substitutes found for this ingredient"]
        else:
            logging.debug(f"Substitutes Error: {response.status_code}, {response.text}")
            return ["No substitutes available"]
    except requests.RequestException as e:
        # Log any network errors and return a fallback message
        logging.debug(f"Substitutes Request Failed: {e}")
        return ["No substitutes available"]

# Find recipes similar to a given recipe for variation suggestions
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
        # Log any errors and return an empty list
        logging.debug(f"Similar Recipes Request Failed: {e}")
        return []