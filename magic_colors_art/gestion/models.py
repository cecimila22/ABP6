from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from decimal import Decimal

# Información del cliente  
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField()

    def __str__(self):
        return self.nombre


# Materiales del producto personalizado para el cliente    
class Material(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    stock = models.PositiveIntegerField(default=0)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, help_text="Impuesto en $")
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def ganancia(self):
        # Ganancia real = precio - costo - impuesto
        return self.precio - self.costo_unitario - self.impuesto

    def precio_suficiente(self):
        # Retorna True si el precio cubre costo + impuesto
        return self.precio >= (self.costo_unitario + self.impuesto)

    def __str__(self):
        return self.nombre   
    
# Los pedidos pueden venir a traves de diferentes canales de venta
class CanalVenta(models.Model):
    TIPO_COSTO_CHOICES = [
        ('FIJO', 'Fijo'),
        ('PORCENTAJE', 'Porcentaje'),
    ]

    nombre = models.CharField(max_length=50)
    tipo_costo = models.CharField(max_length=15, choices=TIPO_COSTO_CHOICES)
    valor_costo = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre    

# Caracterización del producto
class Producto(models.Model):
    nombre = models.CharField(max_length=100,verbose_name="Nombre del producto")
    descripcion = models.TextField(verbose_name="Descripción")
    precio = models.DecimalField(max_digits=8,decimal_places=2,verbose_name="Precio")
    stock = models.PositiveIntegerField(default=0)
           
    def __str__(self):
        return self.nombre
    
# Caracterización del pedido
class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    canal_venta = models.ForeignKey(CanalVenta, on_delete=models.PROTECT)
    fecha = models.DateField(auto_now_add=True)
    referencia_externa = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nombre}"

class ProductoPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="productos")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_cliente = models.DecimalField(max_digits=10, decimal_places=2)

    # Campos internos para control de costos y ganancia
    costo_materiales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_canal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ganancia = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Permite calcular costos pra validación de precio, ya que los productos son personalizados
    def calcular_costos(self):
        # Suma de materiales
        self.costo_materiales = sum([dm.subtotal for dm in self.detalle_materiales.all()])

        # Costo por canal de venta
        if self.pedido.canal_venta.tipo_costo == 'FIJO':
            self.costo_canal = self.pedido.canal_venta.valor_costo
        else:
            self.costo_canal = (self.costo_materiales * self.pedido.canal_venta.valor_costo) / Decimal(100)

        # Costo total y ganancia
        self.costo_total = self.costo_materiales + self.costo_canal
        self.ganancia = self.precio_cliente - self.costo_total
        
    def validar_stock_materiales(self):
        for dm in self.detalle_materiales.all():
            if dm.material.stock < dm.cantidad_usada:
                raise ValueError(f"No hay suficiente stock de {dm.material.nombre}")

    def descontar_stock_materiales(self):
        for dm in self.detalle_materiales.all():
            dm.material.stock -= dm.cantidad_usada
            dm.material.save()

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} (Pedido {self.pedido.id})"
    
class DetalleMaterialProductoPedido(models.Model):
    producto_pedido = models.ForeignKey(ProductoPedido, on_delete=models.CASCADE, related_name="detalle_materiales")
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    cantidad_usada = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Calcula subtotal automáticamente
        self.subtotal = self.cantidad_usada * self.material.costo_unitario
        super().save(*args, **kwargs)
        
# Calcular costos y descontar stock automáticamente
@receiver(post_save, sender=ProductoPedido)
def actualizar_costos_y_stock(sender, instance, created, **kwargs):

    if created:  # solo cuando se crea el producto del pedido
        instance.calcular_costos()
        instance.save(update_fields=['costo_materiales', 'costo_canal', 'costo_total', 'ganancia'])

        instance.validar_stock_materiales()
        instance.descontar_stock_materiales()
    
