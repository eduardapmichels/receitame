from django.shortcuts import render
from receitas.data_handler import data_handler
from receitas.utils import *
RECIPE_STRUCT = struct.Struct("i120si5500si20s4?i")

def index(request):
    context = {

    }
    return render(request, 'home.html', context)

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
            per_page=70,
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



def list_categories(request):
    #para selects
    difficulties = ["easy", "medium", "hard"]
    cuisines = load_all_cuisines()

    # --- Parâmetros do GET ---
    checked_vegan = 'checked_vegan' in request.GET
    checked_vegetarian = 'checked_vegetarian' in request.GET
    checked_gluten = 'checked_gluten' in request.GET
    checked_dairy = 'checked_dairy' in request.GET
    selected_difficulties = request.GET.getlist('difficulty')
    selected_cuisines = request.GET.getlist('cuisine')
    page = int(request.GET.get('page', 1))
    per_page = 70

    # --- Carregar cache dos arquivos invertidos ---
    tags_index_cache = build_tags_index_cache("data")



    # --- Construir lista de tags para intersect ---
    tags = []

    if checked_vegan:
        tags.append("vegan")
    if checked_vegetarian:
        tags.append("vegetarian")
    if checked_gluten:
        tags.append("gluten_free")
    if checked_dairy:
        tags.append("dairy_free")
    
    # Adiciona dificuldades, cuisines e categorias como tags também
    tags += selected_difficulties
    tags += selected_cuisines


    # --- Intersect dos IDs ---
    if tags:
        filtered_ids = intersect_tags(tags, tags_index_cache)
    else:
        # Se nenhum filtro, pega todas as receitas

        
        recipes_bin_path = Path("data/recipes.bin")
        size = recipes_bin_path.stat().st_size
        total_recipes = size // RECIPE_STRUCT.size
        filtered_ids = set(range(1, total_recipes + 1))

    # --- Paginar resultados ---
    recipes_page = paginate(list(filtered_ids), page, per_page)
    total_results = len(filtered_ids)
    total_pages = (total_results + per_page - 1) // per_page

    query_params = request.GET.copy()

    # força remover page para reconstruir nos botões
    if "page" in query_params:
        del query_params["page"]

    # --- Montar contexto ---
    context = {
        "difficulties": difficulties,
        "cuisines": cuisines,
        "recipes": recipes_page,
        "total_results": total_results,
        "page": page,
        "count": total_pages,
        "checked_vegan": checked_vegan,
        "checked_vegetarian": checked_vegetarian,
        "checked_gluten": checked_gluten,
        "checked_dairy": checked_dairy,
        "selected_difficulties": selected_difficulties,
        "selected_cuisines": selected_cuisines,
        "error": None,
        "query_string": query_params.urlencode(),
    }

    return render(request, 'categories.html', context)


def add_recipe(request):
    context = {
    }
    return render(request, 'home.html', context)

def read_recipe(request):
    return

