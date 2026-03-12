import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()


def registro_exitoso(request):
    return render(request, 'gestion/registro_exitoso.html')
