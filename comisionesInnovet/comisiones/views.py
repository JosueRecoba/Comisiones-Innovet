from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import F, Q, Sum, DecimalField
from django.db.models.functions import Coalesce
from django.utils.dateparse import parse_date
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.urls import reverse_lazy
from .models import Cliente, Producto, Vendedor, Factura, ClienteProducto
from decimal import Decimal
from django.shortcuts import redirect
from django.http import HttpResponseNotAllowed
from django.contrib import messages
import json

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
    fields = ['nombre', 'compras_realizadas', 'fecha_registro', 'vendedor']
    success_url = reverse_lazy('cliente-list')

    def form_valid(self, form):
        cliente = form.save(commit=False)
        cliente.save()
        return redirect('cliente-list')
    


class ClienteUpdateView(UpdateView):
    model = Cliente
    template_name = 'comisiones/cliente_form.html'
    fields = ['nombre']
    success_url = reverse_lazy('cliente-list')


class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'comisiones/cliente_confirm_delete.html'
    success_url = reverse_lazy('cliente-list')

# ======= Clientes Producto =======
class ClienteProductoView(TemplateView):
    template_name = "comisiones/cliente_producto.html"

class ComprasView(TemplateView):
    template_name = "comisiones/compras.html"

class FacturasView(TemplateView):
    template_name = "comisiones/facturas.html"

class ProductosView(TemplateView):
    template_name = "comisiones/productos.html"

class VendedorView(View):
    template_name = "comisiones/vendedor.html"

    def get(self, request, *args, **kwargs):
        """
        Maneja la solicitud GET para cargar la página con la lista de vendedores.
        """
        vendedores = Vendedor.objects.all().order_by('nombre')
        return render(request, self.template_name, {'vendedores': vendedores})

    def post(self, request, *args, **kwargs):
        """
        Maneja la solicitud POST para agregar un nuevo vendedor.
        """
        if 'agregar_vendedor' in request.POST:
            nombre = request.POST.get('nombre')
            if nombre:
                if Vendedor.objects.filter(nombre__iexact=nombre).exists():
                    messages.error(request, f"El vendedor '{nombre}' ya existe.")
                else:
                    Vendedor.objects.create(nombre=nombre)
                    messages.success(request, f"Vendedor '{nombre}' agregado con éxito.")
            return redirect('vendedor')
        return HttpResponseNotAllowed(['POST'])

    def put(self, request, *args, **kwargs):
        """
        Maneja la solicitud PUT para actualizar un vendedor.
        """
        vendedor_id = kwargs.get('id')
        data = json.loads(request.body.decode('utf-8'))
        nombre = data.get('nombre')

        if vendedor_id and nombre:
            try:
                vendedor = Vendedor.objects.get(id=vendedor_id)
                vendedor.nombre = nombre
                vendedor.save()
                return JsonResponse({'message': 'Vendedor actualizado exitosamente.'}, status=200)
            except Vendedor.DoesNotExist:
                return JsonResponse({'error': 'El vendedor no existe.'}, status=404)
        return JsonResponse({'error': 'Datos incompletos para actualizar el vendedor.'}, status=400)

    def delete(self, request, *args, **kwargs):
        """
        Maneja la solicitud DELETE para eliminar un vendedor.
        """
        vendedor_id = kwargs.get('id')

        if vendedor_id:
            try:
                vendedor = Vendedor.objects.get(id=vendedor_id)
                vendedor.delete()
                return JsonResponse({'message': 'Vendedor eliminado exitosamente.'}, status=200)
            except Vendedor.DoesNotExist:
                return JsonResponse({'error': 'El vendedor no existe.'}, status=404)
        return JsonResponse({'error': 'ID del vendedor no proporcionado.'}, status=400)

class VentasView(TemplateView):
    template_name = "comisiones/ventas.html"

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
