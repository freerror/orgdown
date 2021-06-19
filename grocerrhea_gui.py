import PySimpleGUI as sg
import random
import string
import pyperclip

class Ingredient:
    def __init__(self, idn, name, filter):
        self.id = idn
        self.name = name
        self.filter = filter
        self.required = False


class Recipe:
    def __init__(self, idn, name, ingredients, status=False, filter=None):
        self.id = idn
        self.name = name
        self.ingredients = ingredients
        self.filter = filter
        self.status = status


def get_required_ingredients(items, recipes, ingredients, required_ingredients):
    # Cull not needed ingredients first
    for recipe in recipes:
        for item in items:
            if item[0] == recipe.name and item[1] == False:
                for ingredient in recipe.ingredients:
                    if any(ingredient == x for x in required_ingredients):
                        print(f'    removing {ingredient} because its in required_ingredients but its not required')
                        required_ingredients.remove(ingredient)
                    
    # Now get new ingredients
    for recipe in recipes:
        for item in items:
            if item[0] == recipe.name and item[1] == True:
                for ingredient in recipe.ingredients:
                    if not ingredient in required_ingredients:
                        print(f'    Adding {ingredient}')
                        required_ingredients.append(ingredient)

    # Cull ingredient items
    for ingredient in ingredients:
        for item in items:
            if item[0] == ingredient.name and item[1] == False:
                if any(ingredient.name == x for x in required_ingredients):
                    print(f'    removing {ingredient.name} because its not selected anymore')
                    required_ingredients.remove(ingredient.name)
        
    # Add required items that ARE ingredients, e.g. snacks
    for ingredient in ingredients:
        for item in items:
            if item[0] == ingredient.name and item[1] == True:
                if not ingredient.name in required_ingredients:
                    print(f'    Adding {ingredient.name}')
                    required_ingredients.append(ingredient.name)
    
    return required_ingredients


def restore_bool_selection(bool_list, flat_list):
    new_bool_list = []
    for item in flat_list:
        if any(item == x[0] and x[1] == False for x in bool_list):
            for bool_item in bool_list:
                if bool_item[0] == item and bool_item[1] == False:
                    print(f"    Found existing selection, setting {item} to false")
                    new_bool_list.append([bool_item[0], False])
        else:
            print(f"    Setting new or unchanged {item} to True")
            new_bool_list.append([item, True])
            
    return new_bool_list


def make_grocery_list(ingredients, item_choices, restock_ingredients):
    output_string = ""
    output_string += '\n=== SHOPPING LIST ===\n'
    output_string += '\nYou need to restock the following ingredients:\n'

    last_section = ''
    for ingredient in ingredients:
        if ingredient.name in restock_ingredients:
            section = ingredient.filter
            if last_section != section:
                output_string += f'\n= {section} =\n'
            last_section = section
            output_string += f'{ingredient.name}\n'
    output_string += '\n=== FYI ===\n'
    output_string += '\nSelected meals and other items:\n\n'
    for choice in item_choices:
        if choice[1] == True:
            output_string += f'{choice[0]}\n'
    output_string += '\n\n'
    return output_string


def open_window(text_to_display):
    output_layout = [[sg.Multiline(text_to_display, size=(80,50), key='output_box')]]
    window = sg.Window('Shopping List', output_layout, modal=True)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
    window.close()


def main():
    ingredients = []
    recipes = []
    required_ingredients = []
    max_recipes = 6
    max_snacks = 4

    
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
    
    # GUI Stuff

    # ------ Make the Table Data ------
    meals_headings = ["Recipe, Snack or Item", "Order it?"]
    snack_headings = ["Item", "Wanted?"]
    item_choices = []
    required_ingredients = []
    bool_ingredients = []
    for meal in recipes:
        item_choices += [[meal.name, meal.status]]
    for snack in ingredients:
        if snack.filter in ('Snacks', 'Health, Cleaning & Pets'):
            item_choices += [[snack.name, False]]

    choices_layout = [
        [sg.Text('Weekly meals, snacks and other items')],
        [sg.Table(values=item_choices, headings=meals_headings, max_col_width=55,
            auto_size_columns=True,
            display_row_numbers=True,
            justification='right',
            num_rows=15,
            key='Recipes_Table',
            row_height=35,
            tooltip='This is the choices table')],
        [sg.Button('Toggle Item')]
                     ]
    restock_layout = [
        [sg.Text('Items that may require restocking')],
        [sg.Table(values=[['', '']], headings=meals_headings, max_col_width=55,
            auto_size_columns=True,
            display_row_numbers=True,
            justification='right',
            num_rows=15,
            key='Restock_Table',
            row_height=35,
            tooltip='This is the restock table')],
        [sg.Button('Toggle Restock'), sg.Button('No *'), sg.Button('Grocerrhea!')]
        
    ]
    layout = [[sg.Column(choices_layout), sg.Column(restock_layout)]]

    sg.theme('Dark')
    window = sg.Window('Grocerrhea', layout)

    colour_select = lambda t, r: window.FindElement(t).Update(row_colors=((r, 'white', 'green'),))
    colour_deselect = lambda t, r: window.FindElement(t).Update(row_colors=((r, 'white', 'grey'),))

    # Event Loop
    while True:
        try:
            event, values = window.Read()

            if event == "Toggle Item":
                print(f"Toggled Item: {item_choices[values['Recipes_Table'][0]][0]}")
                # Use selected row as index within item_choices and toggle that item
                item_choices[values['Recipes_Table'][0]][1] ^= True
                window.FindElement('Recipes_Table').Update(values=item_choices)
                required_ingredients = get_required_ingredients(
                    item_choices,
                    recipes,
                    ingredients,
                    required_ingredients)
                bool_ingredients = restore_bool_selection(bool_ingredients, required_ingredients)
                # Refresh the restock table with the updates and restores
                window.FindElement('Restock_Table').Update(values=bool_ingredients)
                # For each of of the tables, restore the colors
                for row in bool_ingredients:
                    if row[1]:
                        colour_select('Restock_Table', bool_ingredients.index(row))
                    else:
                        colour_deselect('Restock_Table', bool_ingredients.index(row))
                for row in item_choices:
                    if row[1]:
                        colour_select('Recipes_Table', item_choices.index(row))
                    else:
                        colour_deselect('Recipes_Table', item_choices.index(row))
            if event == "Toggle Restock":
                print(f"Toggled Restock for {values['Restock_Table'][0]} aka {bool_ingredients[0][0]}")
                bool_ingredients[values['Restock_Table'][0]][1] ^= True
                window.FindElement('Restock_Table').Update(values=bool_ingredients)
                # Restore colors
                for row in bool_ingredients:
                    if row[1]:
                        print(f"    Colouring {row[0]} (row: {bool_ingredients.index(row)})")
                        colour_select('Restock_Table', bool_ingredients.index(row))
                    else:
                        print(f"    Uncolouring {row[0]} (row: {bool_ingredients.index(row)})")
                        colour_deselect('Restock_Table', bool_ingredients.index(row))
            if event == "No *":
                print("No * selected")
                for i in bool_ingredients:
                    if '*' in i[0]:
                        i[1] = False
                window.FindElement('Restock_Table').Update(values=bool_ingredients)
                # Restore colors
                for row in bool_ingredients:
                    if row[1]:
                        print(f"    Colouring {row[0]} (row: {bool_ingredients.index(row)})")
                        colour_select('Restock_Table', bool_ingredients.index(row))
                    else:
                        print(f"    Uncolouring {row[0]} (row: {bool_ingredients.index(row)})")
                        colour_deselect('Restock_Table', bool_ingredients.index(row))
            elif event == "Grocerrhea!":
                true_ingredients = [x[0] for x in bool_ingredients if x[1] == True]
                shopping_list = make_grocery_list(ingredients, item_choices, true_ingredients)
                print(shopping_list)
                pyperclip.copy(shopping_list)
                open_window(shopping_list)
            elif event == None:
                break
        except IndexError as err:
            print(f"Nothing was selected, causing an {err}... No worries.")
        except KeyError as err:
            print(f"You caused a Key Error for:{err}... No worries.")
            
    window.Close()

if __name__ == '__main__':
    main()