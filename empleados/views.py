from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg
from .models import Empleado
from .formsEmpleados import EmpleadoForm
from libromayor.models import ParametrosGlobales

# --- LISTAR ---
def lista_empleados_view(request):
    empleados = Empleado.objects.all()
    
    # Obtener parámetros globales (necesarios para el JavaScript)
    parametros = ParametrosGlobales.objects.first()
    if not parametros:
        messages.warning(request, "⚠️ Debes configurar primero los Parámetros Globales del sistema.")
        return redirect('parametros_globales')

    # Calcular promedio de costo real por hora
    promedio_costo = empleados.aggregate(
        promedio=Avg('costo_real_hora_ajustado')
    )['promedio'] or 0

    promedio_costo = round(promedio_costo, 4)

    return render(request, 'listaEmpleados.html', {
        'empleados': empleados,
        'promedio_costo': promedio_costo,
        'parametros': parametros,  # ← AGREGADO
    })


# --- CREAR ---
def crear_empleado_view(request):
    form = EmpleadoForm(request.POST or None)

    # Verificar existencia de parámetros globales
    parametros = ParametrosGlobales.objects.first()
    if not parametros:
        messages.warning(request, "⚠️ Debes configurar primero los Parámetros Globales del sistema.")
        return redirect('parametros_globales')

    if request.method == 'POST' and form.is_valid():
        empleado = form.save()
        messages.success(request, f"✅ {empleado.nombre} agregado correctamente.")
        return redirect('lista_empleados')

    return render(request, 'formE.html', {
        'form': form,
        'accion': 'Agregar',
        'parametros': parametros,
    })


# --- EDITAR ---
def editar_empleado_view(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    form = EmpleadoForm(request.POST or None, instance=empleado)

    parametros = ParametrosGlobales.objects.first()
    if not parametros:
        messages.warning(request, "⚠️ Debes configurar primero los Parámetros Globales del sistema.")
        return redirect('parametros_globales')

    if request.method == 'POST' and form.is_valid():
        empleado = form.save()
        messages.success(request, f"✏️ {empleado.nombre} actualizado correctamente.")
        return redirect('lista_empleados')

    return render(request, 'formE.html', {
        'form': form,
        'accion': 'Editar',
        'parametros': parametros,
    })


# --- ELIMINAR ---
def eliminar_empleado_view(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)

    if request.method == 'POST':
        nombre = empleado.nombre
        empleado.delete()
        messages.success(request, f"🗑️ El empleado '{nombre}' fue eliminado correctamente.")
        return redirect('lista_empleados')

    return render(request, 'confirmar_eliminar.html', {'empleado': empleado})