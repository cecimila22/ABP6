from django.shortcuts import render
from .models import Producto, Cliente


def inicio(request):
    return render(request, 'gestion/inicio.html')


def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'gestion/productos.html', {'productos': productos})


def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'gestion/clientes.html', {'clientes': clientes})
