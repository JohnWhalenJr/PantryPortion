import tkinter as tk
from tkinter import ttk, messagebox
from main_refactored import create_account, login, get_filtered_recipes, get_recipe_details_by_id

# -------------------- Dietary Options & Ingredient Categories --------------------

dietary_options = ["Gluten Free", "Keto", "Vegetarian", "Vegan", "Pescetarian", "Paleo"]

ingredient_categories = {
    "Aromatics": ["onions", "garlic", "carrots", "celery", "jalapeños"],
    "Herbs": ["cilantro", "parsley", "dill"],
    "Other Vegetables": ["potatoes", "bell pepper", "greens", "tomatoes"],
    "Acidity": ["lemon", "lime", "vinegar"],
    "Protein": ["chicken", "beef", "turkey", "fish", "eggs"],
    "Dairy": ["milk", "butter", "cheddar cheese", "yogurt", "parmesan"],
    "Pantry Staples": ["black beans", "garbanzo beans", "rice", "pasta"]
}

# -------------------- App Class --------------------

class RecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PantryPortion")
        self.user = None
        self.restrictions = set()
        self.ingredient_list = []

        self.create_login_ui()

    def create_login_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Username:").grid(row=0, column=0, sticky="w")
        self.username_entry = tk.Entry(self.root)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Password:").grid(row=1, column=0, sticky="w")
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.root, text="Login", command=self.handle_login).grid(row=2, column=0)
        tk.Button(self.root, text="Create Account", command=self.handle_create).grid(row=2, column=1)

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, result = login(username, password)
        if success:
            self.user = result
            self.create_search_ui()
        else:
            messagebox.showerror("Login Failed", result)

    def handle_create(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, result = create_account(username, password)
        if success:
            messagebox.showinfo("Account Created", "Account successfully created! Please log in.")
        else:
            messagebox.showerror("Error", result)

    def create_search_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Restrictions
        tk.Label(self.root, text="Dietary Restrictions:").grid(row=0, column=0, sticky="w")
        self.restriction_vars = {}
        for i, option in enumerate(dietary_options):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(self.root, text=option, variable=var, command=self.update_restrictions_preview)
            cb.grid(row=i + 1, column=0, sticky="w")
            self.restriction_vars[option.lower().replace(" ", "-")] = var

        self.restrictions_preview = tk.Label(self.root, text="Selected: None")
        self.restrictions_preview.grid(row=len(dietary_options) + 1, column=0, sticky="w")

        tk.Button(self.root, text="Reset Restrictions", command=self.reset_restrictions).grid(
            row=len(dietary_options) + 2, column=0
        )

        # Ingredient Dropdown
        tk.Label(self.root, text="Select Ingredient:").grid(row=0, column=1, sticky="w")
        self.ingredient_var = tk.StringVar()
        self.ingredient_dropdown = ttk.Combobox(self.root, textvariable=self.ingredient_var, width=30)
        all_ingredients = []
        for group in ingredient_categories.values():
            all_ingredients.extend(group)
        self.ingredient_dropdown['values'] = sorted(set(all_ingredients))
        self.ingredient_dropdown.grid(row=1, column=1)

        tk.Button(self.root, text="Add Ingredient", command=self.add_ingredient).grid(row=1, column=2)

        self.ingredient_preview = tk.Label(self.root, text="Selected: None")
        self.ingredient_preview.grid(row=2, column=1, columnspan=2, sticky="w")

        tk.Button(self.root, text="Search Recipes", command=self.search_recipes).grid(row=3, column=1, pady=5)

        # Results box
        self.result_listbox = tk.Listbox(self.root, width=60, height=10)
        self.result_listbox.grid(row=4, column=0, columnspan=3, pady=10)
        self.result_listbox.bind("<<ListboxSelect>>", self.display_recipe_details)

        self.detail_text = tk.Text(self.root, height=15, width=60, wrap="word")
        self.detail_text.grid(row=5, column=0, columnspan=3)

    def update_restrictions_preview(self):
        selected = [key for key, var in self.restriction_vars.items() if var.get()]
        self.restrictions = set(selected)
        self.restrictions_preview.config(
            text=f"Selected: {', '.join(selected).title() if selected else 'None'}"
        )

    def reset_restrictions(self):
        for var in self.restriction_vars.values():
            var.set(False)
        self.restrictions.clear()
        self.restrictions_preview.config(text="Selected: None")

    def add_ingredient(self):
        ingredient = self.ingredient_var.get().strip().lower()
        if ingredient and ingredient not in self.ingredient_list:
            self.ingredient_list.append(ingredient)
            self.ingredient_preview.config(text=f"Selected: {', '.join(self.ingredient_list)}")
        self.ingredient_var.set("")

    def search_recipes(self):
        self.result_listbox.delete(0, tk.END)
        self.detail_text.delete("1.0", tk.END)
        print("Searching with:", self.ingredient_list, "Restrictions:", self.restrictions) # Test if restrictions are still applied
        recipes, message = get_filtered_recipes(self.ingredient_list, list(self.restrictions))
        print(f"Fetched {len(recipes)} recipes, message: '{message}'")

        if message:
            messagebox.showinfo("Note", message)
        self.recipe_data = {r['title']: r['id'] for r in recipes}
        for title in self.recipe_data.keys():
            self.result_listbox.insert(tk.END, title)

    def display_recipe_details(self, event):
        selection = self.result_listbox.curselection()
        if not selection:
            return
        title = self.result_listbox.get(selection[0])
        recipe_id = self.recipe_data[title]
        details = get_recipe_details_by_id(recipe_id)
        if not details:
            self.detail_text.insert(tk.END, "Unable to load recipe details.")
            return
        instructions = details.get('instructions', 'No instructions provided.')
        ingredients = [i['original'] for i in details.get('extendedIngredients', [])]
        nutrients = details.get('nutrition', {}).get('nutrients', [])

        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert(tk.END, f"Title: {title}\n\n")
        self.detail_text.insert(tk.END, f"Ingredients:\n" + "\n".join(ingredients) + "\n\n")
        self.detail_text.insert(tk.END, f"Instructions:\n{instructions}\n\n")
        self.detail_text.insert(tk.END, f"Nutrients:\n")
        for nutrient in nutrients:
            self.detail_text.insert(tk.END, f"  {nutrient['name']}: {nutrient['amount']} {nutrient['unit']}\n")

# -------------------- Main Execution --------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeApp(root)
    root.mainloop()
