"""
URL configuration for receitame project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from receitas import views
from django.urls import path
from receitas.views import search_recipes
from receitas.views import add_recipe


urlpatterns = [
    path("ajax/search/", search_recipes, name="ajax_search"),
    path("add_recipe/", views.add_recipe, name="add_recipe"),
    path('', views.index, name = "home"),
    path('process_csv/', views.csv_process, name="csvprocess"),
    path('all_recipes/', views.list_all, name="list_all"),
    path('recipe/<int:recipe_id>/', views.read_recipe, name="read_recipe"),
    path('categories/', views.list_categories, name="list_categories"),
]