# PantryPortion

About the Project

PantryPortion is a recipe management application that helps users quickly find delicious recipes based on ingredients and dietary restrictions using a GUI built with Tkinter, and the Spoonacular API for all the recipe data.

## Features
- **User Authentication**: Create accounts and log in to save dietary preferences.
- **Recipe Search**: Find recipes by ingredients and dietary restrictions.
- **Ingredient Substitutes**: Suggest alternatives for ingredients.
- **Recipe Details**: View detailed recipe information, including ingredients, instructions, and nutrition.


## Installation

Install dependencies: 
   * 'pip install requests sqlalchemy html2text fuzzywuzzy python-Levenshtein' 
   * then 'pip install -r requirements.txt'


##How to use

1) Make sure you have python 3 installed
2) Run the app from your terminal: 'python main.py'
3) Login or Create an account: to create an account - enter in a name, followed by a password
4) Select dietary restrictions if applicable, e.g.  vegetarian, vegan, gluten-free, dairy-free
5) Enter the ingredients in your *Pantry*
   * NOTE: Feeling adventurous? Leave 'Select Ingredient' blank, and click 'Search Recipies'. The program will present a variety of random recipes        based on your dietary choices.
6) Browse then click on the delicious recipie of your choice.
7) If no matching recipes are found, the program automatically suggests ingredient substitutes to repeat the process


## File Structure

- `main.py`: 
* Program execution.
* Tkinter-based GUI for recipe search and management.

- `formatting.py`:
* Handles user interaction (login/account creation)
* Recipe searched on available ingredients
* Display matching recipes
* Recipe details and storage

- `core.py`: 
* The core logic for recipe filtering and fuzzy matching.

- `main_refactored.py`: 
* The functions for authentication and recipe handling.

- `helpers.py`: 
Handles functions for filtering and ingredient substitutions.
The bridge-layer between the Spoontacular API and the user-facing elements of the program.

- `models.py`: 
* The handler for local database setup and schema management for the program. It uses SQLite and SQLAlchemy ORM to store and manage
* User Profiles (usename, password, dietary restrictions)
* Recipes (names, ingredients, instructions, nutrition info)

- `api.py`: 
* API interaction with Spoonacular for recipe data
* All key actions are logged to "pantry_portion.log"
* Uses a static Spoontacular API key
* Error Handling for API failures and missing data
* Uses 'html2text' for instruction formatting + regex as a fallback

- `requirements.txt`: 
* Project dependencies.


## Dependencies
- `requests`: For API calls.
- `sqlalchemy`: For database management.
- `html2text`: For cleaning HTML instructions.
- `fuzzywuzzy`: For fuzzy matching ingredients.
- `python-Levenshtein`: For faster fuzzy matching.

## Database
- Uses `pantry.db` to store user profiles and recipe data.
- Schema is automatically updated via `models.py`.

## Logging
- Logs are saved to `pantry_portion.log` for debugging API calls and operations.

## Notes
- Replace the API key in `api.py` with your own Spoonacular API key.





