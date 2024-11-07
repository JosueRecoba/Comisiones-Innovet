# views.py

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Cliente, Producto, Vendedor, Compra 

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
    fields = ['nombre', 'tipo_cliente']  
    success_url = reverse_lazy('cliente-list')

# Vista para actualizar un cliente
class ClienteUpdateView(UpdateView):
    model = Cliente
    template_name = 'comisiones/cliente_form.html'  
    fields = ['nombre', 'tipo_cliente']
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

# Vista para calcular comisiones
def calcular_comisiones(request):
    comision = None

    if request.method == "POST":
        # Obtener los datos del formulario
        vendedor_id = request.POST.get("vendedor")
        cliente_id = request.POST.get("cliente")
        producto_id = request.POST.get("producto")
        cantidad = int(request.POST.get("cantidad", 1))

        # Obtener las instancias de los modelos
        vendedor = get_object_or_404(Vendedor, id=vendedor_id)
        cliente = get_object_or_404(Cliente, id=cliente_id)
        producto = get_object_or_404(Producto, id=producto_id)

        # Crear una instancia de Compra temporal para calcular la comisión
        compra = Compra(cliente=cliente, vendedor=vendedor, producto=producto, cantidad=cantidad)
        comision = compra.calcular_comision()

    # Pasar los vendedores, clientes y productos al formulario
    context = {
        "vendedores": Vendedor.objects.all(),
        "clientes": Cliente.objects.all(),
        "productos": Producto.objects.all(),
        "comision": comision,
    }
    return render(request, "comisiones/calcular_comisiones.html", context)

class DashboardView(TemplateView):
    template_name = 'comisiones/dashboard.html' 