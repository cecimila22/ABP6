from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Cliente, Producto, CanalVenta, Pedido, ProductoPedido
from django.http import JsonResponse

# HOME
def home(request):
    return render(request, 'gestion/home.html')


# CREAR PEDIDO (cliente + pedido en una sola vista)
def crear_pedido(request):
    productos = Producto.objects.all()
    # canales = CanalVenta.objects.filter(activo=True)

    if request.method == "POST":
        # Datos cliente
        nombre = request.POST.get("nombre")
        telefono = request.POST.get("telefono")
        email = request.POST.get("email")
        direccion = request.POST.get("direccion")

        if not nombre or not direccion:
            messages.error(request, "Debes ingresar nombre y dirección del cliente.")
            return render(request, 'gestion/crear_pedido.html', {'productos': productos, 'canales': canales})

        # Crear cliente
        cliente, creado = Cliente.objects.get_or_create(
            telefono=telefono,
            defaults={
                'nombre': nombre,
                'email': email,
                'direccion': direccion
            }
        )
        if not creado:messages.info(request, "Cliente existente encontrado.")
    
        # Datos pedido
        producto_id = request.POST.get("producto")
        
        try:
            cantidad = int(request.POST.get("cantidad", 1))
        except ValueError:
            cantidad = 1

        producto = get_object_or_404(Producto, id=producto_id)

        # Canal automático
        canal, creado = CanalVenta.objects.get_or_create(nombre="Pedidos Web", defaults={"activo": True, 
        "valor_costo": 0})
        
        # Crear pedido
        pedido = Pedido.objects.create(cliente=cliente,canal_venta=canal)

        # Crear producto del pedido
        ProductoPedido.objects.create(pedido=pedido, producto=producto, cantidad=cantidad, precio_cliente=producto.precio)

        # Mensaje de aviso de stock
        if producto.stock < cantidad:
            messages.warning(request, f"Pedido registrado, pero el stock de {producto.nombre} es insuficiente. Puede tardar más tiempo en ser entregado.")

        # Descontar stock si hay suficiente
        else:
            producto.stock -= cantidad
            producto.save()

        messages.success(request, "Pedido creado exitosamente.")

        return redirect('pedido_exitoso', pedido_id=pedido.id)

    return render(request, 'gestion/crear_pedido.html', {
    'productos': productos
    })
        
# VER PEDIDOS 
@staff_member_required
def ver_pedidos(request):
    pedidos = Pedido.objects.select_related('cliente', 'canal_venta').all().order_by('-fecha')
    return render(request, 'gestion/ver_pedidos.html', {'pedidos': pedidos})

# PEDIDO EXITOSO  
def pedido_exitoso(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    return render(request, 'gestion/pedido_exitoso.html', {'pedido': pedido})

# PÁGINA PRODUCTOS
def productos(request):
    return render(request, 'gestion/productos.html')

# PÁGINA CONTACTO
def contacto(request):
    return render(request, 'gestion/contacto.html')

# BUSCAR CLIENTE
def buscar_cliente(request):
    telefono = request.GET.get('telefono')

    try:
        cliente = Cliente.objects.get(telefono=telefono)

        data = {
            "nombre": cliente.nombre,
            "email": cliente.email,
            "direccion": cliente.direccion
        }

    except Cliente.DoesNotExist:
        data = {}

    return JsonResponse(data)