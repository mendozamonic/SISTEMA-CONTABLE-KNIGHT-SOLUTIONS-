from django.contrib import admin
from django.urls import path

# Importa tus apps con alias únicos
from libromayor import views as libromayor_views
from estadosfinancieros import views as estados_views
from empleados import views as empleados_views



urlpatterns = [
    path('admin/', admin.site.urls),

    # --- Módulo Libro Mayor (contabilidad general) ---
    path('', libromayor_views.catalogo_cuentas_view, name='catalogo_cuentas'),
    path('transacciones/', libromayor_views.crear_asiento_contable_view, name='transacciones'),
    path('cuentas_por_tipo/', libromayor_views.cuentas_por_tipo, name='cuentas_por_tipo'),

    # --- Períodos contables ---
    path('periodos/', libromayor_views.lista_periodos_view, name='periodo_contable'),
    path('periodos/nuevo/', libromayor_views.crear_periodo_view, name='crear_periodo'),
    path('periodos/<int:pk>/editar/', libromayor_views.editar_periodo_view, name='editar_periodo'),
    path('periodos/<int:pk>/cerrar/', libromayor_views.cerrar_periodo_view, name='cerrar_periodo'),

    # --- Estados financieros (nuevo módulo) ---
    path('libro-mayor/', estados_views.libro_mayor_view, name='libro_mayor'),
    path('balance-general/', estados_views.balance_general_view, name='balance_general'),
    path('estado-resultados/', estados_views.estado_resultados_view, name='estado_resultados'),
    path('cambio-patrimonial/', estados_views.cambio_patrimonial_view, name='cambio_patrimonial'),

    # ----- Parametros Globales -----
    path('parametros/', libromayor_views.parametros_globales_view, name='parametros_globales'), 


    # ----- Costos Indirectos -----
    path('costos-indirectos/', libromayor_views.lista_costos_indirectos_view, name='lista_costos_indirectos'),
    path('costos-indirectos/nuevo/', libromayor_views.crear_costo_indirecto_view, name='crear_costo_indirecto'),
    path('costos-indirectos/<int:pk>/editar/', libromayor_views.editar_costo_indirecto_view, name='editar_costo_indirecto'),
    path('costos-indirectos/<int:pk>/eliminar/', libromayor_views.eliminar_costo_indirecto_view, name='eliminar_costo_indirecto'),


    # ----- Empleados-----
    path('empleados/', empleados_views.lista_empleados_view, name='lista_empleados'),
    path('empleados/nuevo/', empleados_views.crear_empleado_view, name='crear_empleado'),
    path('empleados/<int:pk>/editar/', empleados_views.editar_empleado_view, name='editar_empleado'),
    path('empleados/<int:pk>/eliminar/', empleados_views.eliminar_empleado_view, name='eliminar_empleado'),


]
