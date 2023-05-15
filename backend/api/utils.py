from recipe.models import Component


def ingredients_set(recipe, ingredients_data):
    Component.objects.bulk_create([Component(
        ingredient=ingredient['ingredient'],
        recipe=recipe,
        amount=ingredient['amount']
    ) for ingredient in ingredients_data])


def create_content(ingredients):
    content = 'Ваш список покупок:\n'

    for ingredient in ingredients:
        content += (f"{ingredient['ingredient__name']} " + 
                    f"({ingredient['ingredient__measurement_unit']}) " + 
                    f"{ingredient['amount']}" +
                    '\n')
    return content
