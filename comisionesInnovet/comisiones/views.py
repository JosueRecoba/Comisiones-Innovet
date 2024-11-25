from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.utils.dateparse import parse_date
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Cliente, Producto, Vendedor, Compra, Factura, ClienteProducto, Comision
from decimal import Decimal
from datetime import datetime


# Vista para listar todos los clientes
class ClienteListView(ListView):
    model = Cliente
    template_name = 'comisiones/cliente_list.html'
    context_object_name = 'clientes'

# Vista para detalles de un cliente
class ClienteDetailView(DetailView):
    model = Cliente
    template_name = 'comisiones/cliente_detail.html'
    context_object_name = 'cliente'

# Vista para crear un nuevo cliente
class ClienteCreateView(CreateView):
    model = Cliente
    template_name = 'comisiones/cliente_form.html'
    fields = ['nombre']
    success_url = reverse_lazy('cliente-list')

# Vista para actualizar un cliente
class ClienteUpdateView(UpdateView):
    model = Cliente
    template_name = 'comisiones/cliente_form.html'
    fields = ['nombre']
    success_url = reverse_lazy('cliente-list')

# Vista para eliminar un cliente
class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'comisiones/cliente_confirm_delete.html'
    success_url = reverse_lazy('cliente-list')

# Vista para listar todos los productos
class ProductoListView(ListView):
    model = Producto
    template_name = 'comisiones/producto_list.html'
    context_object_name = 'productos'

# Vista para detalles de un producto
class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'comisiones/producto_detail.html'
    context_object_name = 'producto'

# Vista para crear un nuevo producto
class ProductoCreateView(CreateView):
    model = Producto
    template_name = 'comisiones/producto_form.html'
    fields = ['nombre', 'tipo_producto', 'precio']
    success_url = reverse_lazy('producto-list')

# Vista para actualizar un producto
class ProductoUpdateView(UpdateView):
    model = Producto
    template_name = 'comisiones/producto_form.html'
    fields = ['nombre', 'tipo_producto', 'precio']
    success_url = reverse_lazy('producto-list')

# Vista para eliminar un producto
class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = 'comisiones/producto_confirm_delete.html'
    success_url = reverse_lazy('producto-list')

# Vista para listar todas las compras
class CompraListView(ListView):
    model = Compra
    template_name = 'comisiones/compra_list.html'
    context_object_name = 'compras'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar lógica para calcular las comisiones
        for compra in context['compras']:
            compra.comision_calculada = compra.calcular_comision()
        return context

# Vista para detalles de una compra
class CompraDetailView(DetailView):
    model = Compra
    template_name = 'comisiones/compra_detail.html'
    context_object_name = 'compra'

# Vista para crear una nueva compra
class CompraCreateView(CreateView):
    model = Compra
    template_name = 'comisiones/compra_form.html'
    fields = ['cliente', 'vendedor', 'producto', 'cantidad']
    success_url = reverse_lazy('compra-list')

# Vista para actualizar una compra
class CompraUpdateView(UpdateView):
    model = Compra
    template_name = 'comisiones/compra_form.html'
    fields = ['cliente', 'vendedor', 'producto', 'cantidad']
    success_url = reverse_lazy('compra-list')

# Vista para eliminar una compra
class CompraDeleteView(DeleteView):
    model = Compra
    template_name = 'comisiones/compra_confirm_delete.html'
    success_url = reverse_lazy('compra-list')

# vista para calcular comisiones
def calcular_comisiones(request):
    # Obtener filtros del usuario
    cliente_id = request.GET.get('cliente')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Validar y parsear fechas
    if fecha_inicio:
        try:
            fecha_inicio = parse_date(fecha_inicio)
        except ValueError:
            fecha_inicio = None
    if fecha_fin:
        try:
            fecha_fin = parse_date(fecha_fin)
        except ValueError:
            fecha_fin = None

    # Crear el filtro de manera condicional usando Q
    filtros = Q(estatus_pago='Pagada')
    if cliente_id:
        filtros &= Q(cliente_id=cliente_id)
    if fecha_inicio:
        filtros &= Q(fecha_pago__gte=fecha_inicio)
    if fecha_fin:
        filtros &= Q(fecha_pago__lte=fecha_fin)

    # Filtrar las facturas con los filtros generados
    facturas = Factura.objects.select_related('cliente').prefetch_related('compras').filter(filtros)

    # Calcular comisiones
    for factura in facturas:
        subtotal = Decimal('0.00')
        for compra in factura.compras.all():
            compra.comision = compra.calcular_comision()
            subtotal += compra.producto.precio * compra.cantidad
            compra.save()

        factura.subtotal = subtotal
        factura.total_comision = sum(compra.comision for compra in factura.compras.all())
        factura.save()

    # Obtener todos los clientes
    clientes = Cliente.objects.all()

    context = {
        'clientes': clientes,
        'facturas': facturas,
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d') if fecha_inicio else '',
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d') if fecha_fin else '',
    }
    return render(request, 'comisiones/calcular_comisiones.html', context)
# Vista para el dashboard
class DashboardView(TemplateView):
    template_name = 'comisiones/dashboard.html'
