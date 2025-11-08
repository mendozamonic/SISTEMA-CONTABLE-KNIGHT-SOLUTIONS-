from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('empleados/', include('empleados.urls')),
    
    # Comentar las rutas que aún no tienen vistas definidas
    # path('empleados/registrar/', views.registrar_empleado, name='registrar_empleado'), 
    # path('empleados/modificar/<int:pk>/', views.modificar_empleado, name='modificar_empleado'),
    # path('empleados/eliminar/<int:pk>/', views.eliminar_empleado, name='eliminar_empleado'),
]