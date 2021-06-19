class Ingredient:
    def __init__(self, idn, name, filter):
        self.id = idn
        self.name = name
        self.filter = filter
        self.required = False


class Recipe:
    def __init__(self, idn, name, ingredients, filter=None):
        self.id = idn
        self.name = name
        self.ingredients = ingredients
        self.filter = filter


def choices_query(prompt, items, max_items, filter=None):
    restart_choices = True
    while restart_choices:
        print(f'\n{prompt} [note: r restarts choices dialog]\n')
        choices = []
        cur_item = 0
        for item in items:
            if item.filter == filter:
                choices_progress = f'{choices.__len__()}/{max_items}'
                items_progress = f'{cur_item + 1}/{items.__len__()}'
                current_choice = input(f'[Chosen {choices_progress}] {items_progress} {item.name}? Answer [y/n/r]: ').lower()
                while current_choice not in ('y', 'n', 'r'):
                    current_choice = input(f'Previous input invalid, did you want {item.name}? Answer [y/n]: ').lower()
                if current_choice == 'y':
                    choices.append(item.id)
                elif current_choice == 'r':
                    print("Restarting this dialog...")
                    break
                # No need to continue if already chosen all meals
                if choices.__len__() == max_items:
                    restart_choices = False
                    break
                cur_item += 1
        if current_choice != 'r':
            if choices.__len__() < max_items:
                print("You didn't pick enough, try again, or quit...")
            elif choices.__len__() > max_items:
                print("You picked too many, try again, or quit...")
            else:
                choices_progress = f'{choices.__len__()}/{max_items}'
                print(f'[Chosen {choices_progress}] Chosen!')
                restart_choices = False
    return choices


def main():
    print('=== Grocerrhea Weekly Grocery Planner ===')
    ingredients = []
    recipes = []
    required_ingredients = []
    max_recipes = int(input("How many meals do you need to plan? [Enter whole number]: "))
    max_snacks = int(input("How many snacks do you need to plan? [Enter whole number]: "))

    
    # Parse the Ingredients
    with open('ingredients.cfg', 'r') as f:
        content = f.read()[2:]
        counter = 0
        for section in content.split('# '):
            section_name = section.split('\n')[0]
            for ingredient in section.split('\n')[1:]:
                if ingredient != '':
                    ingredients.append(Ingredient(counter, ingredient, section_name))
                    counter += 1
    
    # Parse the Recipes
    with open('recipes.cfg', 'r') as f:
        content = f.read()[2:]
        counter = 0
        for recipe in content.split('# '):
            recipe_name = recipe.split('\n')[0]
            recipe_ingredients = []
            for ingredient in recipe.split('\n')[1:]:
                if ingredient != '':
                    recipe_ingredients.append(ingredient)
            recipes.append(Recipe(counter, recipe_name, recipe_ingredients))
            counter += 1
    
    # Parse input to choose recipe choices
    choices = choices_query("Make your meal choices for this week:\n\nWould you like to have...", recipes, max_recipes)

    # Parse Snacks
    snack_choices = choices_query("Make your snack choice for this week:\n\nWould you like to have...", ingredients, max_snacks, "Snacks")
    
    # Determine required groceries
    print(f'\nYour choices this week:')
    for choice in choices:
        rec = recipes[choice]
        print(rec.name)
        for ingredient in rec.ingredients:
            if ingredient not in required_ingredients:
                required_ingredients.append(ingredient)
    
    for snack in snack_choices:
        snek = ingredients[snack]
        print(snek.name)
        if snek.name not in required_ingredients:
            required_ingredients.append(snek.name)
    

    # Gather input on which groceries to restock
    restart_restock = True
    while restart_restock:
        restock_ingredients = []
        print('\nDo you need to restock... [note: r restarts restock dialog]')
        print("(Batch items)")
        for ingredient in required_ingredients:
            if ingredient.find('*') == -1:
                needs_restock = input(f'{ingredient}? Answer [y/n/r]: ').lower()
                while needs_restock not in ('y', 'n', 'r'):
                    needs_restock = input(f'Previous input invalid, restock {ingredient}? Answer [y/n]: ')
                if needs_restock == 'y':
                    restock_ingredients.append(ingredient)
                elif needs_restock == 'r':
                    print("Restarting restock dialog...")
                    break
        print("\n(Bulk items)")
        for ingredient in required_ingredients:
            if ingredient.find('*') != -1:
                needs_restock = input(f'{ingredient}? Answer [y/n/r]: ').lower()
                while needs_restock not in ('y', 'n', 'r'):
                    needs_restock = input(f'Previous input invalid, restock {ingredient}? Answer [y/n]: ')
                if needs_restock == 'y':
                    restock_ingredients.append(ingredient)
                elif needs_restock == 'r':
                    print("Restarting restock dialog...")
                    break
        if needs_restock != 'r':
            restart_restock = False
            
    
    # Print the grocery list
    print('\nYou need to restock the following ingredients:')
    
    print('\n=== SHOPPING LIST ===')

    last_section = ''
    for ingredient in ingredients:
        if ingredient.name in restock_ingredients:
            section = ingredient.filter
            if last_section != section:
                print(f'\n== {section} ==')
            last_section = ingredient.filter
            print(f'{ingredient.name}')
    print('\n=== MEALS ===')
    for choice in choices:
        rec = recipes[choice]
        print(rec.name)
    print('\n=== Snacks ===')
    for snack in snack_choices:
        snek = ingredients[snack]
        print(snek.name)
    print('\n\n')
        
    

if __name__ == '__main__':
    main()