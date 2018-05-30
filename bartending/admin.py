from django.contrib import admin
from .models import Direction, Drink, Ingredient, Serving, Recipe

admin.site.register(Direction)
admin.site.register(Drink)
admin.site.register(Ingredient)
admin.site.register(Serving)
admin.site.register(Recipe)

