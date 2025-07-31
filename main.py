import csv
from models import UserProfile, Recipe, session
from api import fetch_recipes, fetch_random_recipes, fetch_recipe_details, fetch_substitutes, fetch_similar_recipes
from helpers import suggest_substitution, filter_by_restrictions
import logging

# Setup logging
logging.basicConfig(filename='pantry_portion.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

def main():
    print("\n=== Welcome to PantryPortion! ===")
    
    action = input("Login (l) or Create account (c)? ").lower()
    if action == 'c':
        name = input("Enter username: ")
        existing_user = session.query(UserProfile).filter_by(name=name).first()
        if existing_user:
            print(f"Username '{name}' already exists. Please choose a different username or login.")
            return
        password = input("Enter password: ")
        restrictions = input("Enter dietary restrictions (comma-separated, e.g., vegetarian,vegan,gluten-free, or leave blank): ") or None
        user = UserProfile(name=name, password=password, dietary_restrictions=restrictions)
        session.add(user)
        try:
            session.commit()
            with open('users.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([name, password, restrictions or ''])
            print(f"Account created! Dietary restrictions: {restrictions or 'None'}")
        except Exception as e:
            print(f"Error creating account: {e}")
            session.rollback()
            return
    elif action == 'l':
        name = input("Enter username: ")
        password = input("Enter password: ")
        user = session.query(UserProfile).filter_by(name=name, password=password).first()
        if user:
            print(f"Login successful! Dietary restrictions: {user.dietary_restrictions or 'None'}")
            restrictions = user.dietary_restrictions
        else:
            print("Invalid credentials.")
            return
    else:
        print("Invalid choice.")
        return
    
    while True:
        ingredients = input("\nEnter ingredients (comma-separated, or leave blank for random recipes): ").split(",") if input else []
        ingredients = [i.strip() for i in ingredients if i.strip()]
        
        # Use user input directly
        matched_ingredients = ingredients
        logging.debug(f"Matched Ingredients: {matched_ingredients}")
        
        # Fetch recipes
        if matched_ingredients:
            recipes = fetch_recipes(matched_ingredients)
            # Temporarily bypass filtering for debugging
            filtered_recipes = recipes  # filter_by_restrictions(recipes, restrictions)
        else:
            filtered_recipes = fetch_random_recipes(restrictions)
        
        # Display recipes
        print("\n=== Available Recipes ===")
        if filtered_recipes:
            for i, recipe in enumerate(filtered_recipes, 1):
                print(f"{i} {recipe['title']}")
        else:
            print("No recipes found. Try different ingredients or fewer restrictions.")
            if ingredients:
                print("\n=== Ingredient Substitutions ===")
                for ingredient in ingredients:
                    subs = suggest_substitution(ingredient)
                    print(f"{ingredient}: {subs}")
            retry = input("\nTry different ingredients or restrictions? (y/n): ").lower()
            if retry != 'y':
                return
            continue
        
        # Allow user to select a recipe
        while True:
            try:
                choice = input("\nEnter the number of the recipe to view details (or 'q' to quit): ")
                if choice.lower() == 'q':
                    return
                choice = int(choice)
                if 1 <= choice <= len(filtered_recipes):
                    selected_recipe = filtered_recipes[choice - 1]
                    details = fetch_recipe_details(selected_recipe['id'])
                    if details:
                        nutrients = {n['name']: n['amount'] for n in details.get('nutrition', {}).get('nutrients', [])}
                        # Store in database
                        session.add(Recipe(
                            name=details['title'],
                            ingredients=",".join([i['name'] for i in details.get('extendedIngredients', [])]),
                            instructions=details.get('instructions', 'No instructions available'),
                            calories=nutrients.get('Calories', 0),
                            protein=nutrients.get('Protein', 0),
                            fat=nutrients.get('Fat', 0),
                            carbs=nutrients.get('Carbohydrates', 0)
                        ))
                        session.commit()
                        
                        # Display details
                        print(f"\n=== Recipe: {details['title']} ===")
                        print("Ingredients:")
                        for ing in details.get('extendedIngredients', []):
                            print(f"- {ing['original']}")
                        print("\nInstructions:")
                        print(details.get('instructions', 'No instructions available'))
                        # Display similar recipes as variations
                        similar = fetch_similar_recipes(details['id'])
                        if similar:
                            print("\nVariations:")
                            for s in similar[:3]:
                                print(f"- {s['title']} (ready in {s['readyInMinutes']} min)")
                        print("\nNutritional Info:")
                        print(f"Calories: {nutrients.get('Calories', 0)}")
                        print(f"Protein: {nutrients.get('Protein', 0)}")
                        print(f"Fat: {nutrients.get('Fat', 0)}")
                        print(f"Carbs: {nutrients.get('Carbohydrates', 0)}")
                        if ingredients:
                            print("\n=== Ingredient Substitutions ===")
                            for ingredient in ingredients:
                                subs = suggest_substitution(ingredient)
                                print(f"{ingredient}: {subs}")
                    else:
                        print("Failed to fetch recipe details.")
                else:
                    print(f"Please enter a number between 1 and {len(filtered_recipes)}.")
            except ValueError:
                print("Invalid input. Enter a number or 'q' to quit.")
            break

if __name__ == "__main__":
    main()
