from django.urls import path
from . import views

urlpatterns = [
    path('all_drinks', views.all_drinks, name='all_drinks'),
    path('', views.all_drinks, name='all_drinks'),
    path('mybar', views.mybar, name='my_bar'),
    path('favorites', views.favorites, name='favorites'),
    path('random', views.random, name='random'),
    path('drink/<int:index>/', views.single_drink, name='single_drink'),
    path('signup', views.signup.as_view(), name='signup'),
    path('add_favorite/<int:index>', views.add_favorite, name='add_favorite'),
    path('delete_favorite/<int:index>', views.delete_favorite, name='delete_favorite'),
    path('remove_from_bar/<int:index>', views.remove_from_bar, name='remove_from_bar'),
    path('add_ingredient', views.add_ingredient, name='add_ingredient'),
    path('remove_from_bar/add_ingredient', views.add_ingredient, name='add_ingredient'),
    path('calculate_possible_drinks', views.calculate_possible_drinks, name='calculate_possible_drinks'),
]