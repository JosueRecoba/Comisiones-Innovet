from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import F, Q, Sum, DecimalField
from django.db.models.functions import Coalesce
from django.utils.dateparse import parse_date
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Cliente, Producto, Vendedor, Factura, ClienteProducto
from decimal import Decimal


# ======= Clientes =======
class ClienteListView(ListView):
    model = Cliente
    template_name = 'comisiones/cliente_list.html'
    context_object_name = 'clientes'


class ClienteDetailView(DetailView):
    model = Cliente
    template_name = 'comisiones/cliente_detail.html'
    context_object_name = 'cliente'


class ClienteCreateView(CreateView):
    model = Cliente
    template_name = 'comisiones/cliente_form.html'
    fields = ['nombre']
    success_url = reverse_lazy('cliente-list')


class ClienteUpdateView(UpdateView):
    model = Cliente
    template_name = 'comisiones/cliente_form.html'
    fields = ['nombre']
    success_url = reverse_lazy('cliente-list')


class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'comisiones/cliente_confirm_delete.html'
    success_url = reverse_lazy('cliente-list')


class ClienteProductoView(TemplateView):
    template_name = "comisiones/cliente_producto.html"

class ComprasView(TemplateView):
    template_name = "comisiones/compras.html"

class FacturasView(TemplateView):
    template_name = "comisiones/facturas.html"

class ProductosView(TemplateView):
    template_name = "comisiones/productos.html"

class VendedorView(TemplateView):
    template_name = "comisiones/vendedor.html"

class VentasView(TemplateView):
    template_name = "comisiones/ventas.html"


# ======= Comisiones =======
def calcular_comisiones(request):
    cliente_id = request.GET.get('cliente')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Filtro de fechas
    if fecha_inicio and isinstance(fecha_inicio, str):
        try:
            fecha_inicio = parse_date(fecha_inicio)
        except ValueError:
            fecha_inicio = None
    else:
        fecha_inicio = None

    if fecha_fin and isinstance(fecha_fin, str):
        try:
            fecha_fin = parse_date(fecha_fin)
        except ValueError:
            fecha_fin = None
    else:
        fecha_fin = None

    # Filtra solo facturas con estatus PAGADA
    filtros = Q(estatus_pago='Pagada')
    if cliente_id:
        filtros &= Q(cliente_id=cliente_id)
    if fecha_inicio:
        filtros &= Q(fecha_pago__gte=fecha_inicio)
    if fecha_fin:
        filtros &= Q(fecha_pago__lte=fecha_fin)

    # Consultar facturas con sus relaciones
    facturas = Factura.objects.select_related('cliente').prefetch_related('compras').filter(filtros)

    # Calcular comisiones y subtotales para cada factura
    for factura in facturas:
        subtotal = factura.compras.aggregate(
            total=Coalesce(Sum(F('producto__precio') * F('cantidad'), output_field=DecimalField()), Decimal('3.00'))
        )['total']
        factura.subtotal = subtotal
        factura.total_comision = sum(compra.calcular_comision() for compra in factura.compras.all())
        factura.save()

    # Pasar contexto a la plantilla
    context = {
        'clientes': Cliente.objects.all(),
        'facturas': facturas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'comisiones/calcular_comisiones.html', context)


def detalle_factura(request, folio):
    facturas = Factura.objects.select_related('cliente', 'cliente__vendedor').prefetch_related('compras__producto').filter(folio=folio)
    datos_facturas = []

    for factura in facturas:
        for compra in factura.compras.all():
            # Cálculo del porcentaje de comisión
            comision_monto = float(compra.comision) * 100
            
            # Cálculo del monto de la comisión en dinero
            monto_comision = compra.comision * compra.producto.precio * compra.cantidad  # Ejemplo

            datos_facturas.append({
                'folio': factura.folio,
                'cliente': factura.cliente.nombre,
                'estatus': factura.estatus,
                'subtotal': factura.subtotal,
                'estatus_pago': factura.estatus_pago,
                'fecha_pago': factura.fecha_pago,
                'tipo_producto': compra.producto.tipo_producto,
                'nombre_producto': compra.producto.nombre,
                'compras_realizadas': factura.cliente.compras_realizadas,
                'tipo_cliente': ClienteProducto.objects.filter(cliente=factura.cliente).first().tipo_cliente,
                'comision': comision_monto,  
                'monto_comision': monto_comision, 
                'vendedor': factura.cliente.vendedor.nombre,
            })

    return render(request, 'comisiones/detalle_factura.html', {'datos_facturas': datos_facturas})


class DashboardView(TemplateView):
    template_name = 'comisiones/dashboard.html'
