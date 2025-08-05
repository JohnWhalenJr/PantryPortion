PantryPortion

About the Project
The user should be able to navigate the program to find a recipe that meets their current pantry holdings and whatevery restrictions or preferences that they may have.

main.py
The main interface and control flow for the program.
* Handles user interaction (login/account creation)
* Recipe searched on available ingredients
* Display matching recipes
* Recipe details and storage

api.py
The backend utility that helps users find meals based on the ingredients they have. It connects to the Spoontacular API and includes funcitonality to search for recipes, clean and display instructions, find substitutes, and suggest similar recipes.
* All key actions are logged to "pantry_portion.log"
* Uses a static Spoontacular API key
* Error Handling for API failures and missing data
* Uses 'html2text' for instruction formatting + regex as a fallback

models.py
The handler for local database setup and schema management for the program. It uses SQLite and SQLAlchemy ORM to store and manage
1) User Profiles (usename, password, dietary restrictions)
2) Recipes (names, ingredients, instructions, nutrition info)

helpers.py
The bridge-layer between the Spoontacular API and the user-facing elements of the program.
Functions for dietary filtering and ingredient substitution.

How to use
1) Make sure you have python 3 installed
2) Install dependencies: 'pip install requests sqlalchemy html2text fuzzywuzzy python-Levenshtein'
3) Run the app from your terminal: 'python main.py'
4) Login or Create an account: to create an account - enter in a name, followed by a password
5) Enter in dietary restrictions e.g.  vegetarian, vegan, gluten-free, dairy-free
6) Enter the ingredients in your *Pantry*
 * If you leave it blank, the program will show random recipes based on your dietary choices in step 5
7) Browse recipe suggestions
8) Select the corresponding number to view details of your choice
9) The recipe details are automatically saved to your local database after selection
10) If no matching recipes are found, the program automatically suggests ingredient substitutes to repeat the process