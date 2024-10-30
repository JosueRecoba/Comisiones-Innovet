from django.contrib import admin
from .models import Cliente, Producto, Vendedor, Compra

admin.site.register(Cliente)
admin.site.register(Producto)
admin.site.register(Vendedor)
admin.site.register(Compra)
