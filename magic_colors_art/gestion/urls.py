from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('crear-pedido/', views.crear_pedido, name='crear_pedido'),
    path('ver-pedidos/', views.ver_pedidos, name='ver_pedidos'),
    path('pedido-exitoso/<int:pedido_id>/', views.pedido_exitoso, name='pedido_exitoso'),
    path('buscar-cliente/', views.buscar_cliente, name='buscar_cliente'),
    path('productos/', views.productos, name='productos'),
    path('contacto/', views.contacto, name='contacto'),
]