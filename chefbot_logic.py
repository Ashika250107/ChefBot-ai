def suggest_dishes(recipes, ingredients):
    possible = []
    for dish in recipes:
        if any(item in dish["ingredients"] for item in ingredients):
            possible.append(dish)
    return possible
