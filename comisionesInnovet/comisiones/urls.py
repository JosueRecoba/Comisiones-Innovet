from django.urls import path
from . import views
from .views import (
    ClienteListView, ClienteDetailView, ClienteCreateView, 
    ClienteUpdateView, ClienteDeleteView, 
    calcular_comisiones, DashboardView,
    ComprasView, VentasView, VendedorView, 
    FacturasView, ClienteProductoView, ProductosView
)

urlpatterns = [
    # --------------------- URLs de Clientes ---------------------
    path('clientes/', ClienteListView.as_view(), name='cliente-list'),
    path('clientes/<int:pk>/', ClienteDetailView.as_view(), name='cliente-detail'),
    path('clientes/nuevo/', ClienteCreateView.as_view(), name='cliente-create'),
    path('clientes/<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente-update'),
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente-delete'),
    
    # --------------------- URLs de Detall Factura ---------------------
    
    path('factura/<str:folio>/', views.detalle_factura, name='detalle_factura'),

    # --------------------- URLs de Dashboard ---------------------
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # --------------------- URLs de Facturas ---------------------
    path('facturas/', FacturasView.as_view(), name='facturas'),

    # --------------------- URLs de Compras (Nuevas) ---------------------
    path('compras/', ComprasView.as_view(), name='compras'),

    # --------------------- URLs de Ventas ---------------------
    path('ventas/', VentasView.as_view(), name='ventas'),

    # --------------------- URLs de Vendedor ---------------------
    path('vendedor/', VendedorView.as_view(), name='vendedor'),

    # --------------------- URLs de Comisiones ---------------------
    path('calcular-comisiones/', views.calcular_comisiones, name='calcular-comisiones'),

    # --------------------- URLs de Productos ---------------------
    path('productos/', ProductosView.as_view(), name='productos'),

    # --------------------- URLs de Cliente Productos ---------------------
    path('cliente-producto/', views.ClienteProductoView.as_view(), name='cliente-producto'),

]
