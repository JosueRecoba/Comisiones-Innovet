from django.db import models
from django.utils import timezone
from decimal import Decimal

CLIENTE_TIPO_CHOICES = [
    ('N', 'Nuevo'),
    ('E', 'Estable'),
    ('H', 'Histórico'),
]

PRODUCTO_TIPO_CHOICES = [
    ('B', 'Blister'),
]

ESTATUS_FACTURA_CHOICES = [
    ('Emitida', 'Emitida'),
    ('Cancelada', 'Cancelada'),
]

ESTATUS_PAGO_CHOICES = [
    ('Pagada', 'Pagada'),
    ('Pendiente', 'Pendiente'),
]

class Vendedor(models.Model):
    nombre = models.TextField()

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    nombre = models.TextField()
    compras_realizadas = models.PositiveIntegerField(default=0)
    fecha_registro = models.DateTimeField(default=timezone.now)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)


    def actualizar_tipo_cliente(self):
        """
        Actualiza el estado del cliente según las compras realizadas.
        """
        cliente_producto = ClienteProducto.objects.filter(cliente=self).first()
        if cliente_producto:
            if self.compras_realizadas >= 6 and cliente_producto.tipo_cliente == 'N':
                cliente_producto.tipo_cliente = 'E'
            elif cliente_producto.tipo_cliente == 'E' and self.ha_pasado_un_anio():
                cliente_producto.tipo_cliente = 'H'
            cliente_producto.save()

    def ha_pasado_un_anio(self):
        """
        Verifica si ha pasado un año desde que el cliente fue clasificado como Estable.
        """
        return timezone.now() > self.fecha_registro + timezone.timedelta(days=365)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    nombre = models.TextField()
    tipo_producto = models.CharField(max_length=1, choices=PRODUCTO_TIPO_CHOICES, default='B')
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.nombre} ({self.cliente.nombre})'


class Compra(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_compra = models.DateTimeField(default=timezone.now)
    factura = models.ForeignKey('Factura', on_delete=models.CASCADE, related_name='compras', null=True, blank=True)
    comision = models.DecimalField(max_digits=10, decimal_places=2, default=0.03)

    def calcular_comision(self):
        # Busca el tipo de cliente en ClienteProducto
        cliente_producto = ClienteProducto.objects.filter(cliente=self.cliente, producto=self.producto).first()
        if not cliente_producto:
            return Decimal('0.03')  

        # Define el porcentaje basado en el tipo de cliente
        porcentaje_comision = {
            'N': Decimal('3.00'),  
            'E': Decimal('2.00'),  
            'H': Decimal('1.00'),  
        }.get(cliente_producto.tipo_cliente, Decimal('0.00'))

        # Calcula la comisión
        return (self.producto.precio * self.cantidad * porcentaje_comision) / 100

    def save(self, *args, **kwargs):
        # Calcula la comisión antes de guardar
        self.comision = self.calcular_comision()
        super().save(*args, **kwargs)

        # Actualiza las compras realizadas y el tipo de cliente
        self.cliente.compras_realizadas += 1
        self.cliente.actualizar_tipo_cliente()

    def __str__(self):
        return f'Compra de {self.producto.nombre} por {self.cliente.nombre}'


class ClienteProducto(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo_cliente = models.CharField(max_length=1, choices=CLIENTE_TIPO_CHOICES, default='N')

    def __str__(self):
        return f'{self.cliente.nombre} - {self.producto.nombre} ({self.tipo_cliente})'


class Factura(models.Model):
    folio = models.CharField(max_length=20, unique=True, db_index=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    estatus = models.CharField(max_length=10, choices=ESTATUS_FACTURA_CHOICES, default='Emitida')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    estatus_pago = models.CharField(max_length=10, choices=ESTATUS_PAGO_CHOICES, default='Pendiente')
    fecha_pago = models.DateField(null=True, blank=True)

    def calcular_comisiones(self):
        """
        Calcula el total de comisiones para los productos de esta factura.
        """
        total_comision = sum(
            compra.comision * compra.cantidad for compra in self.compras.all()
        )
        return total_comision

    def __str__(self):
        return f'Factura {self.folio} - {self.cliente.nombre}'


class Venta(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_venta = models.DateField(default=timezone.now)

    def __str__(self):
        return f'Venta de {self.producto.nombre} - Factura {self.factura.folio}'