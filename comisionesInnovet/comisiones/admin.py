from django.contrib import admin
from .models import Cliente, Producto, Vendedor, Compra, ClienteProducto, Factura, Venta

admin.site.register(Cliente)
admin.site.register(Producto)
admin.site.register(Vendedor)
admin.site.register(Compra)
admin.site.register(ClienteProducto)
admin.site.register(Factura)
admin.site.register(Venta)
