from django.apps import AppConfig
from receitas.utilitario.init_trie import rebuild_trie



class ReceitasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'receitas'

    def ready(self):
        rebuild_trie()  # isso roda quando o servidor inicia