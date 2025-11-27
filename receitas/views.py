from django.shortcuts import render
from receitas.data_handler import data_handler
from receitas.utils import *


def index(request):
    context = {

    }
    return render(request, 'home.html', context)
# Create your views here.


def csv_process(request):
    result = data_handler()  # aqui roda todo o CSV
    
    context = {
        "total_recipes": result["total_recipes"],
        "elapsed_time": result["time"],
        "message": result["message"]
    }
    return render(request, 'home.html', context)


def list_all(request):


    # página
    page = int(request.GET.get("page", 1))

    # checkbox
    checked = request.GET.get("check") is not None

    
    # lê valores min e max se checkbox estiver marcado
    if checked:
        bt = load_btree_pickle()
        min_time = parse_int(request.GET.get("min"))
        max_time = parse_int(request.GET.get("max"))

        # Correções
        if min_time is not None and min_time < 0:
            min_time = 0

        if max_time is not None and max_time < 0:
            max_time = 0

        # Se ambos existem e min > max → inverte
        if min_time is not None and max_time is not None:
            if min_time > max_time:
                min_time, max_time = max_time, min_time
        pages_max, recipes, total_r_found =get_recipes_page_bt(
            bt,
            page=page,
            per_page=200,
            min_time=min_time,
            max_time=max_time
        )

    else:
        trie=load_trie_pickle()
        min_time = None
        max_time = None
        pages_max, recipes, total_r_found =get_recipes_page_trie(
            trie,
            page=page,
            per_page=200,
        )
  


    query_params = request.GET.copy()

    # força remover page para reconstruir nos botões
    if "page" in query_params:
        del query_params["page"]

    context = {
        "recipes": recipes,
        "page": page,
        "count": pages_max,
        "total_results": total_r_found,
        "checked": checked,
        "min": min_time,
        "max": max_time,
        "query_string": query_params.urlencode(),
    }
     

    return render(request, "list_recipes.html", context)


def read_recipe(request):
    return

def list_vegan(request):
    context = {}
    return render(request, 'home.html', context)
def list_vegetarian(request):
    context = {}
    return render(request, 'home.html', context)
def list_gluten_free(request):
    context = {

    }
    return render(request, 'home.html', context)
def list_dairy_free(request):
    context = {
    }
    return render(request, 'home.html', context)

def list_cuisines(request):
    context = {

    }
    return render(request, 'home.html', context)

def list_easy(request):
    context = {

    }
    return render(request, 'home.html', context)
def list_medium(request):
    context = {

    }
    return render(request, 'home.html', context)
def list_difficult(request):
    context = {

    }
    return render(request, 'home.html', context)

def list_categories(request):
    context = {
    }
    return render(request, 'home.html', context)
