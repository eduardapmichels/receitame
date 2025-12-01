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


urlpatterns = [
    path('', views.index, name = "home"),
    path('process_csv/', views.csv_process, name="csvprocess"),
    path('all_recipes/', views.list_all, name="list_all"),
    #path('all_recipes_time/', views.list_time, name="list_time"),
    path('recipe/<int:recipe_id>/', views.read_recipe, name="read_recipe"),
    path('vegan/', views.list_vegan, name="list_vegan"),
    path('vegetarian/', views.list_vegetarian, name="list_vegetarian"),
    path('dairy_free/', views.list_dairy_free, name="list_dairy_free"),
    path('gluten_free/', views.list_gluten_free, name="list_gluten_free"),
    path('easy/', views.list_easy, name="list_easy"),
    path('medium/', views.list_medium, name="list_medium"),
    path('difficult/', views.list_difficult, name="list_difficult"),
    path('cuisines/', views.list_cuisines, name="list_cuisines"),
]

