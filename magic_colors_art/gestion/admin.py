from django.contrib import admin
from .models import Cliente, Pedido, Producto, Material, CanalVenta, DetalleMaterialPedido

admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(Producto)
admin.site.register(Material)
admin.site.register(CanalVenta)
admin.site.register(DetalleMaterialPedido)
