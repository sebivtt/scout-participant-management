from food import models as food_models


class PriceModule:

    def setPriceInPackage(self, price):
        packages_set = food_models.Package.objects.filter(id=price.package.id)
        print('setPriceInPackage')  # noqa: T201
        for package in packages_set:
            package.price_per_kg=price.price_per_kg
            package.save()

            portions_set = food_models.Portion.objects.filter(ingredient=package.portion.ingredient)
            print('setPriceInPortion')  # noqa: T201
            for portion in portions_set:
                print(portion)  # noqa: T201
                portion.price_per_kg=package.price_per_kg
                portion.save()

                recipe_item_set = food_models.RecipeItem.objects.all()

                for recipe_item in recipe_item_set:
                    if (recipe_item.portion == portion):
                        recipe_item.price_per_kg=portion.price_per_kg
                        recipe_item.save()
            print('setIngredientPrice')  # noqa: T201
            ingredient = food_models.Ingredient.objects.filter(id=package.portion.ingredient.id).first()
            ingredient.price_per_kg=price.price_per_kg
            ingredient.save()