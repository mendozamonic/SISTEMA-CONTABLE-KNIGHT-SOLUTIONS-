"""
URL configuration for SIC project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from libromayor import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.catalogo_cuentas_view, name='catalogo_cuentas'),
    path('transacciones/', views.crear_asiento_contable_view, name='transacciones'),
    path('cuentas_por_tipo/', views.cuentas_por_tipo, name='cuentas_por_tipo'),

    path('periodos/', views.lista_periodos_view, name='periodo_contable'),
    path('periodos/nuevo/', views.crear_periodo_view, name='crear_periodo'),
    path('periodos/<int:pk>/editar/', views.editar_periodo_view, name='editar_periodo'),
    path('periodos/<int:pk>/eliminar/', views.eliminar_periodo_view, name='eliminar_periodo'),
    path('periodos/<int:pk>/cerrar/', views.cerrar_periodo_view, name='cerrar_periodo'),

]


