# empleados/urls.py
# empleados/urls.py
from django.urls import path
from . import views

app_name = 'empleados'

urlpatterns = [
    # path raíz de la aplicación (que será '/empleados/' gracias a include)
    path('', views.lista_empleados, name='lista_empleados'), 
    path('registrar/', views.registrar_empleado, name='registrar_empleado'),
]