from django.db import models
from django.contrib.auth.models import User

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
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=50)

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
class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    canal_venta = models.ForeignKey(CanalVenta, on_delete=models.PROTECT)
    fecha = models.DateField(auto_now_add=True)

    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    costo_materiales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_canal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ganancia = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    referencia_externa = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nombre}"

    # Calculo de costos del productos personalizados
    def calcular_costos(self):
        materiales = self.materiales.all()
        self.costo_materiales = sum(m.subtotal for m in materiales)

        if self.canal_venta.tipo_costo == 'FIJO':
            self.costo_canal = self.canal_venta.valor_costo
        else:
            self.costo_canal = (self.costo_materiales * self.canal_venta.valor_costo) / 100

        self.costo_total = self.costo_materiales + self.costo_canal
        self.ganancia = self.precio_venta - self.costo_total
        self.save()   
       
# Cada pedido puede tener materialles diferentes, por ser ajustado a necesidades del cliente    
class DetalleMaterialPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='materiales')
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    cantidad_usada = models.DecimalField(max_digits=10, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad_usada * self.costo_unitario
        super().save(*args, **kwargs)    
             
class Producto(models.Model):
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre del producto"
    )
    descripcion = models.TextField(verbose_name="Descripción")
    precio = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Precio"
    )
    stock = models.PositiveIntegerField(verbose_name="Stock disponible")


    def __str__(self):
        return self.nombre



    


    