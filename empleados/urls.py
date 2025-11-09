# empleados/urls.py
# empleados/urls.py
from django.urls import path
from . import views

app_name = 'empleados'

urlpatterns = [
    # path raíz de la aplicación (que será '/empleados/' gracias a include)
    path('', views.tabla_empleados, name='tabla_empleados'), 
    path('registro_empleado/', views.registro_empleado, name='registro_empleado'),
    path('tabla_empleados/', views.tabla_empleados, name='tabla_empleados'),
]