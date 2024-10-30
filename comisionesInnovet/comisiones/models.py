from django.db import models
from django.utils import timezone

# Tipo de cliente
CLIENTE_TIPO_CHOICES = [
    ('N', 'Nuevo'),
    ('E', 'Estable'),
    ('H', 'Histórico'),
]

# Tipo de producto
PRODUCTO_TIPO_CHOICES = [
    ('B', 'Blister'),
]

class Cliente(models.Model):
    nombre = models.TextField()  
    tipo_cliente = models.CharField(max_length=1, choices=CLIENTE_TIPO_CHOICES, default='N')  
    compras_realizadas = models.PositiveIntegerField(default=0)
    fecha_registro = models.DateTimeField(default=timezone.now)  

    def actualizar_tipo_cliente(self):
        """
        Actualiza el estado del cliente según las compras realizadas.
        """
        if self.compras_realizadas >= 6 and self.tipo_cliente == 'N':
            self.tipo_cliente = 'E'
        elif self.tipo_cliente == 'E' and self.ha_pasado_un_anio():
            self.tipo_cliente = 'H'
        self.save()

    def ha_pasado_un_anio(self):
        """
        Verifica si ha pasado un año desde que el cliente fue clasificado como Estable.
        """
        return timezone.now() > self.fecha_registro + timezone.timedelta(days=365)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.TextField()  
    tipo_producto = models.CharField(max_length=1, choices=PRODUCTO_TIPO_CHOICES, default='B')  
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.nombre} ({self.tipo_producto})'


class Vendedor(models.Model):
    nombre = models.TextField()  

    def __str__(self):
        return self.nombre


class Compra(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_compra = models.DateTimeField(default=timezone.now)  

    def calcular_comision(self):
        """
        Calcula la comisión para el vendedor basada en el tipo de cliente.
        """
        porcentaje_comision = 0
        if self.cliente.tipo_cliente == 'N':
            porcentaje_comision = 0.03  # 3% para clientes nuevos
        elif self.cliente.tipo_cliente == 'E':
            porcentaje_comision = 0.02  # 2% para clientes estables
        elif self.cliente.tipo_cliente == 'H':
            porcentaje_comision = 0.01  # 1% para clientes históricos

        return self.producto.precio * self.cantidad * porcentaje_comision

    def save(self, *args, **kwargs):
        """
        Al guardar la compra, actualizamos el estado del cliente si es necesario.
        """
        super().save(*args, **kwargs)
        self.cliente.compras_realizadas += 1
        self.cliente.actualizar_tipo_cliente()

    def __str__(self):
        return f'Compra de {self.producto.nombre} por {self.cliente.nombre}'
