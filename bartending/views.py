from django.http import HttpResponse
from django.shortcuts import render
from .models import *
from random import randint
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.csrf import csrf_protect

LOAD_PAGE_RESULTS_COUNT = 10
DEFAULT_SEARCH_RESULTS_COUNT = 25

def all_drinks(request):
    # incoming parameter of search term determines results, blank means show all
    search_text = (request.GET['search_text'] if 'search_text' in request.GET else None)
    
    if search_text:
        results = query_drinks(search_text=search_text, limit=DEFAULT_SEARCH_RESULTS_COUNT)
        results_limited = (len(results) == DEFAULT_SEARCH_RESULTS_COUNT)
    else:
        results = query_drinks(search_text=None, limit=LOAD_PAGE_RESULTS_COUNT)
        results_limited = True
    
    return render(request, 'bartending/tabs.html', 
        { 'username': get_username(request), 'active': 'all_drinks',
          'results': results, 'results_limited': results_limited })

def mybar(request):
    items = list()
    username = None
    not_in_bar = None
    if request.user.is_authenticated:
        username = get_username(request)
        ingredient_ids = MyBar.objects.filter(user=request.user).values_list('ingredient')
        for ingredient_id in ingredient_ids:
            items.append(Ingredient.objects.get(id=ingredient_id[0]))
        
        all_ingredients = Ingredient.objects.order_by('name')
        not_in_bar = set(all_ingredients) - set(items)
    return render(request, 'bartending/tabs.html', { 'username': username, 'active': 'my_bar', 'items': items, 'not_in_bar': not_in_bar })

def favorites(request):
    if request.user.is_authenticated:
        username = get_username(request)
        results = get_user_favorites(request)
    else:
        username = None
        results = list()
    return render(request, 'bartending/tabs.html', { 'username': username, 'active': 'favorites', 'results': results })

def random(request):
    random_drink = Drink.objects.get(id=randint(1, Drink.objects.count() + 1))
    directions = get_drink_directions(random_drink.id)

    return render(request, 'bartending/tabs.html', { 'username': get_username(request), 'active': 'random',
                           'name': random_drink.name, 'directions': directions, 'id': random_drink.id, 
                           'favorite': get_is_favorite(request, random_drink.id) })

def single_drink(request, index):
    drink = Drink.objects.get(id=index)
    directions = get_drink_directions(index)
    return render(request, 'bartending/tabs.html', { 'username': get_username(request), 
        'active': 'drink', 'name': drink.name, 'directions': directions, 'id': index,
        'favorite': get_is_favorite(request, index) })

def add_favorite(request, index):
    # ensure drink is not already favorited
    if not get_is_favorite(request, index): 
        new_fav = Favorite(drink=Drink.objects.get(id=index), user=request.user)
        new_fav.save()
    return single_drink(request, index)

def delete_favorite(request, index):
    # check drink is actually favorited
    if get_is_favorite(request, index):
        old_fav = Favorite.objects.get(drink=Drink.objects.get(id=index), user=request.user)
        old_fav.delete()
    return single_drink(request, index)

def remove_from_bar(request, index):
    if get_is_in_bar(request, index):
        # old_ingredient = Ingredient.objects.get(id=index)
        old_mybar_entry = MyBar.objects.get(user=request.user, ingredient__id=index)
        old_mybar_entry.delete()
    return mybar(request)

def add_ingredient(request):
    if request.is_ajax() and request.user.is_authenticated:
        name = request.POST.get('name', '')
        match = Ingredient.objects.get(name=name)
        
        new_entry = MyBar()
        new_entry.ingredient = match
        new_entry.user = request.user
        new_entry.save()
    return mybar(request)

def calculate_possible_drinks(request):
    on_hand = set([tuple[0] for tuple in MyBar.objects.filter(user=request.user).values_list('ingredient')])
    results = drinks_with_ingredients(on_hand)
    return render(request, 'bartending/drink_results.html', { 'results': results })

class signup(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

# What is django convention for functions which perform processing for view, but aren't views
# themselves? Do they belong in a different file, if so where?

def get_username(request):
    if request.user.is_authenticated:
        return request.user.username
    else:
        return None

def get_drink_ingredients(drink_id):
    ingredient_text = ""
    ingredients = Recipe.objects.filter(drink=drink_id).filter(ingredient__gt=0).values_list('ingredient')
    if len(ingredients) > 0:
        for i in range(0, min(3, len(ingredients))):
            ingredient_text += Ingredient.objects.get(id=ingredients[i][0]).name
            if i == min(3, len(ingredients)) - 1:
                ingredient_text += " ..."
            else:
                ingredient_text += ", "
    return ingredient_text

def query_drinks(search_text=None, limit=LOAD_PAGE_RESULTS_COUNT):
    results = list() # format: [ {'id': 3, name': 'Rum and Coke', 'ingredients': 'Rum, ice, coke...'}, ... ]

    if search_text == None: # not a search, just default rendering of page. List first N drinks of db
        # get all drinks, first three ingredients (if 3 exist), link to url for each page
        for drink in Drink.objects.all():
            if len(results) >= limit:
                break
            ingredient_text = get_drink_ingredients(drink.id)
            results.append({ 'id': drink.id, 'name': drink.name, 'ingredients': ingredient_text })
    else:
        # look for name matches when searching
        search_words = search_text.lower().split(" ")
        for drink in Drink.objects.all():
            if len(results) >= limit:
                break
            
            string_match = False
            for word in search_words:
                if word in drink.name.lower():
                    string_match = True
                    break
            if string_match:
                ingredient_text = get_drink_ingredients(drink.id)
                results.append({ 'id': drink.id, 'name': drink.name, 'ingredients': ingredient_text })

    return results

def get_drink_directions(drink_id):
    steps = Recipe.objects.filter(drink=drink_id).order_by('steporder')
    directions = list() # format: [ {direction: "shake...", children: ["ice cube", "1oz gin"]} ]
    cur_dir = None
    for step in steps:
        if step.direction != 0: # it's a direction
            if cur_dir == None: # this is the first direction
                cur_dir = dict()
            else:
                directions.append(cur_dir)
            
            cur_dir = { 'direction': Direction.objects.get(id=step.direction).instruction,
                        'children': [] }
        else:
            serving = Serving.objects.get(id=step.serving).measurement
            ingredient = Ingredient.objects.get(id=step.ingredient).name
            cur_dir['children'].append(serving + " " + ingredient)

    if (type(cur_dir) is dict) and ('children' in cur_dir) and (len(cur_dir['children']) > 0):
        directions.append(cur_dir)
    
    return directions

def get_user_favorites(request):
    results = list()
    queryset = Favorite.objects.filter(user=request.user)
    for res in queryset:
        results.append({ 'id': res.drink.id, 'name': res.drink.name,
                         'ingredients': get_drink_ingredients(res.drink.id) })
    return results

def get_is_favorite(request, id):
    if not request.user.is_authenticated:
        return None
    return len(Favorite.objects.filter(user=request.user, drink=Drink.objects.get(id=id))) > 0

def get_is_in_bar(request, index):
    if not request.user.is_authenticated:
        return None
    return len(MyBar.objects.filter(user=request.user, ingredient__id=index)) > 0

def drinks_with_ingredients(ingredients): # incoming variable is a set of ingredient id's 
    results = list()
    for drink in Drink.objects.all():
        recipe = Recipe.objects.filter(drink=drink.id)
        ingredient_ids = set()
        for direction in recipe:
            if direction.ingredient > 0 :
                ingredient_ids.add(direction.ingredient)
        if ingredient_ids <= ingredients:
            ingredient_text = get_drink_ingredients(drink.id)
            results.append({ 'id': drink.id, 'name': drink.name, 'ingredients': ingredient_text })
    return results
