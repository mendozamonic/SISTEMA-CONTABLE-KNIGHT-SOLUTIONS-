# empleados/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Empleado 
from .forms import EmpleadoForm # Importa el formulario que acabas de crear
from django.urls import reverse


# (Mantener la función lista_empleados tal como la definimos antes)
def tabla_empleados(request):
    empleados_qs = Empleado.objects.all().order_by('nombre')
    contexto = {'empleados': empleados_qs}
    # **IMPORTANTE:** El campo costo_real_ajustado de tu HTML debe cambiarse
    # al nombre real del modelo: costo_real_hora_ajustado
    return render(request, 'empleados/tabla_empleados.html', contexto)


def registro_empleado(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            try:
                # When .save() is called, the Empleado model's save method
                # automatically runs all the payroll calculations before committing to the DB.
                empleado = form.save() 
                print(f"Empleado guardado exitosamente: {empleado.nombre} (ID: {empleado.pk})")
                return redirect('empleados:tabla_empleados') # Redirect to the data display view
            except Exception as e:
                print(f"Error al guardar empleado: {e}")
                # Si hay un error, mostrar el formulario con el error
                # El error se mostrará en el template si form.non_field_errors está configurado
                pass
    else:
        form = EmpleadoForm()
        
    return render(request, 'empleados/registrar_empleado.html', {'form': form, 'page_title': 'Registrar Empleado'})


def modificar_empleado(request, pk):
    """
    Vista para modificar un empleado existente.
    Similar a registro_empleado pero con una instancia del modelo.
    """
    empleado = get_object_or_404(Empleado, pk=pk)
    
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            try:
                # When .save() is called, the Empleado model's save method
                # automatically runs all the payroll calculations before committing to the DB.
                empleado = form.save()
                print(f"Empleado modificado exitosamente: {empleado.nombre} (ID: {empleado.pk})")
                return redirect('empleados:tabla_empleados')
            except Exception as e:
                print(f"Error al modificar empleado: {e}")
                pass
    else:
        form = EmpleadoForm(instance=empleado)
    
    return render(request, 'empleados/registrar_empleado.html', {
        'form': form, 
        'page_title': f'Modificar Empleado: {empleado.nombre}'
    })

    
@require_POST
def eliminar_empleado(request, pk): 
    
    # 1. Buscar el objeto (Empleado) o devolver 404
    empleado = get_object_or_404(Empleado, pk=pk)
    
    # 2. Borrar el objeto
    empleado.delete()
    
    # 3. Redirigir al usuario de vuelta a la lista de empleados
    return redirect(reverse('empleados:tabla_empleados'))