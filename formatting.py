# main.py (CLI wrapper)
from main_refactored import (
    login,
    create_account,
    get_filtered_recipes,
    get_recipe_details_by_id,
    get_substitutes_for_ingredients,
    get_similar_recipes
)

def main():
    print("🍽️  Welcome to PantryPortion CLI!")
    user = None

    while not user:
        print("\n[1] Login\n[2] Create Account\n[3] Exit")
        choice = input("Choose an option: ")
        
        if choice == "1":
            username = input("Username: ")
            password = input("Password: ")
            success, result = login(username, password)
            if success:
                user = result
                print(f"\n✅ Welcome back, {user.name}!")
            else:
                print("❌", result)
        
        elif choice == "2":
            username = input("Choose a username: ")
            password = input("Choose a password: ")
            restrictions = input("Any dietary restrictions (comma-separated, or leave blank): ")
            restrictions_list = [r.strip().title() for r in restrictions.split(",") if r.strip()]
            success, result = create_account(username, password, restrictions_list)
            if success:
                user = result
                print(f"\n✅ Account created. Welcome, {user.name}!")
            else:
                print("❌", result)
        
        elif choice == "3":
            print("👋 Goodbye!")
            return
        
        else:
            print("Invalid choice.")

    # After login
    while True:
        print("\n[1] Search Recipes\n[2] View Substitutes\n[3] Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            ingredients = input("Enter ingredients (comma-separated): ").split(",")
            ingredients = [i.strip() for i in ingredients if i.strip()]
            recipes, note = get_filtered_recipes(ingredients, user.dietary_restrictions or [])
            if note:
                print(f"⚠️  {note}")
            
            if not recipes:
                print("❌ No recipes found.")
                continue
            
            print("\n📋 Recipes Found:")
            for idx, recipe in enumerate(recipes):
                print(f"[{idx}] {recipe['title']}")
            
            selection = input("View details? Enter number or skip: ")
            if selection.isdigit():
                idx = int(selection)
                if 0 <= idx < len(recipes):
                    recipe_id = recipes[idx]['id']
                    details = get_recipe_details_by_id(recipe_id)
                    print(f"\n🍲 {details['title']}")
                    print("📝 Ingredients:")
                    for ing in details['extendedIngredients']:
                        print(f"- {ing['originalString']}")
                    print("\n📖 Instructions:")
                    print(details.get('instructions', 'No instructions available'))
                else:
                    print("Invalid selection.")
        
        elif choice == "2":
            ingredients = input("Enter ingredients (comma-separated): ").split(",")
            ingredients = [i.strip() for i in ingredients if i.strip()]
            subs = get_substitutes_for_ingredients(ingredients)
            print("\n🔄 Substitutes:")
            for ing, sub in subs.items():
                print(f"- {ing} → {sub}")
        
        elif choice == "3":
            print("👋 Logged out. Goodbye!")
            break

        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
