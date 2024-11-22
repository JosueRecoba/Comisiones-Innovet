from django.urls import path
from . import views
from .views import (
    ClienteListView, ClienteDetailView, ClienteCreateView, 
    ClienteUpdateView, ClienteDeleteView, 
    ProductoListView, ProductoDetailView, ProductoCreateView,
    ProductoUpdateView, ProductoDeleteView,
    CompraListView, CompraDetailView, CompraCreateView,
    CompraUpdateView, CompraDeleteView,
    calcular_comisiones,  DashboardView
)

urlpatterns = [
    path('clientes/', ClienteListView.as_view(), name='cliente-list'),
    path('clientes/<int:pk>/', ClienteDetailView.as_view(), name='cliente-detail'),
    path('clientes/nuevo/', ClienteCreateView.as_view(), name='cliente-create'),
    path('clientes/<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente-update'),
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente-delete'),
    path('productos/', ProductoListView.as_view(), name='producto-list'),
    path('productos/<int:pk>/', ProductoDetailView.as_view(), name='producto-detail'),
    path('productos/nuevo/', ProductoCreateView.as_view(), name='producto-create'),
    path('productos/<int:pk>/editar/', ProductoUpdateView.as_view(), name='producto-update'),
    path('productos/<int:pk>/eliminar/', ProductoDeleteView.as_view(), name='producto-delete'),
    path('compras/', CompraListView.as_view(), name='compra-list'),
    path('compras/<int:pk>/', CompraDetailView.as_view(), name='compra-detail'),
    path('compras/nuevo/', CompraCreateView.as_view(), name='compra-create'),
    path('compras/<int:pk>/editar/', CompraUpdateView.as_view(), name='compra-update'),
    path('compras/<int:pk>/eliminar/', CompraDeleteView.as_view(), name='compra-delete'),
    path('calcular-comisiones/', views.calcular_comisiones, name='calcular-comisiones'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
