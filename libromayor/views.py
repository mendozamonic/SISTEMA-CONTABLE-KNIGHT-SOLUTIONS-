

from django.shortcuts import render, redirect, get_object_or_404
from .models import Cuenta

from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from .forms import AsientoContableForm, DetalleAsientoFormSet ,PeriodoContableForm
from .models import AsientoContable, DetalleAsiento, Cuenta, PeriodoContable
from django.http import JsonResponse


def catalogo_cuentas_view(request):
    
    # 1. Obtenemos todas las cuentas, ordenadas por su código.
    #    Esto es crucial para que la jerarquía se muestre correctamente.
    cuentas_list = Cuenta.objects.order_by('codigo')
    
    # 2. Procesamos la lista para añadir el nivel de indentación
    cuentas_procesadas = []
    for cuenta in cuentas_list:
        
        # 3. Calculamos el "nivel" contando los puntos.
        #    '1.' -> Nivel 1 (1 punto)
        #    '1.1.' -> Nivel 2 (2 puntos)
        #    '1.1.01.' -> Nivel 3 (3 puntos)
        #    '1.1.01.01.' -> Nivel 4 (4 puntos)
        nivel = cuenta.codigo.count('.')
        
        # 4. Calculamos el padding (espacio a la izquierda)
        #    Restamos 1 para que el Nivel 1 no tenga padding.
        #    Multiplicamos por 25px (puedes ajustar este valor).
        padding_px = nivel * 15
        
        # 5. Determinamos si es una "cuenta de grupo" (para el estilo)
        #    Asumimos que las cuentas de nivel 1 y 2 son grupos (como en tu imagen)
        es_grupo = (nivel <= 2)
        
        cuentas_procesadas.append({
            'cuenta': cuenta,
            'padding': padding_px,
            'es_grupo': es_grupo
        })

    # 6. Enviamos los datos procesados a la plantilla
    context = {
        'cuentas_procesadas': cuentas_procesadas
    }
    
    # Asegúrate de que el nombre de la plantilla sea correcto
    return render(request, 'catalogo_cuentas.html', context)


def crear_asiento_contable_view(request):

 
    periodo_activo = PeriodoContable.objects.order_by('-inicio').first()
    if not periodo_activo or periodo_activo.cerrado:
        messages.warning(
            request,
            "⚠️ No hay ningún período contable activo. Debe crear uno antes de registrar un asiento."
        )
        return redirect('periodo_contable')  # Redirige a la vista para crear un nuevo período

    
    if request.method == 'POST':
        asiento_form = AsientoContableForm(request.POST)
        detalle_formset = DetalleAsientoFormSet(request.POST, prefix='detalles')

        print("---- DEPURANDO VALIDACIONES ----")
        print("asiento_form.is_valid():", asiento_form.is_valid())
        print("detalle_formset.is_valid():", detalle_formset.is_valid())

        if not asiento_form.is_valid():
            print("\n❌ Errores en AsientoContableForm:")
            print(asiento_form.errors.as_json())
            if asiento_form.non_field_errors():
                print("⚠️ Errores generales:", asiento_form.non_field_errors())

        if not detalle_formset.is_valid():
            print("\n❌ Errores en DetalleAsientoFormSet:")
            print(detalle_formset.errors)
            if detalle_formset.non_form_errors():
                print("⚠️ Errores generales del formset:", detalle_formset.non_form_errors())
            for i, form in enumerate(detalle_formset.forms):
                if form.errors:
                    print(f"➡️ Formulario #{i + 1} errores:")
                    print(form.errors.as_json())
        print("---------------------------------\n")

            


        # Valida ambos formularios al mismo tiempo
        if asiento_form.is_valid() and detalle_formset.is_valid():
            
            total_debe = Decimal('0.00')
            total_haber = Decimal('0.00')

            # 1. Validar la DUALIDAD DE LA PARTIDA
            for form in detalle_formset:
                # Los datos ya están limpios y validados por el formset
                monto = form.cleaned_data.get('monto', Decimal('0.00'))
                tipo_monto = form.cleaned_data.get('tipo_monto')

                if tipo_monto == 'Debe':
                    total_debe += monto
                elif tipo_monto == 'Haber':
                    total_haber += monto
            
            # 2. Aplicar las reglas contables
            if total_debe != total_haber:
                # Error: No hay partida doble
                messages.error(
                    request, 
                    f"Error de Dualidad: La partida no está balanceada. "
                    f"Total Debe: ${total_debe:,.2f} | Total Haber: ${total_haber:,.2f}"
                )
            
            elif total_debe == Decimal('0.00'):
                # Error: Monto cero
                messages.error(request, "Error: El monto total del asiento no puede ser cero.")

            else:
                # 3. Guardar todo en una transacción atómica
                try:
                    with transaction.atomic():
                        # Guardar la cabecera (AsientoContable)
                        # El form ya validó la fecha vs el período
                        # Como 'proyecto_relacionado' no está en el form,
                        # se guardará como NULL (gracias a null=True, blank=True en el modelo)
                        asiento = asiento_form.save() 

                        # Guardar cada línea (DetalleAsiento)
                        for form in detalle_formset:
                            cuenta = form.cleaned_data['cuenta']
                            monto = form.cleaned_data['monto']
                            tipo_monto = form.cleaned_data['tipo_monto']

                            # Convertimos de 'tipo_monto' a campos 'debe'/'haber'
                            monto_debe = monto if tipo_monto == 'Debe' else Decimal('0.00')
                            monto_haber = monto if tipo_monto == 'Haber' else Decimal('0.00')

                            DetalleAsiento.objects.create(
                                asiento=asiento,
                                cuenta=cuenta,
                                debe=monto_debe,
                                haber=monto_haber
                            )
                            messages.success(request, f"Éxito: Asiento Contable #{asiento.id} guardado correctamente.")
                        # Redirigir a una vista de "libro diario" o similar
                        return redirect('catalogo_cuentas') # Asegúrate de que esta URL exista

                except Exception as e:
                    messages.error(request, f"Error inesperado al guardar: {e}")

        else:
            # Formularios no válidos
            messages.error(request, "Error: Revise los datos del formulario. Hay campos inválidos.")

    else:
        # Petición GET: Mostrar formularios vacíos
        asiento_form = AsientoContableForm()
        detalle_formset = DetalleAsientoFormSet(prefix='detalles')

    context = {
        'asiento_form': asiento_form,
        'detalle_formset': detalle_formset,
    }
    # Asegúrate de que esta plantilla exista
    return render(request, 'transacciones.html', context)



def cuentas_por_tipo(request):
    tipo = request.GET.get('tipo')
    cuentas = Cuenta.objects.filter(tipo_cuenta=tipo, es_imputable=True).order_by('codigo')
    data = [
        {'id': c.id, 'texto': f"{c.codigo} - {c.nombre}"} # type: ignore
        for c in cuentas
    ]
    return JsonResponse({'cuentas': data})



def lista_periodos_view(request):
    periodos_abiertos = PeriodoContable.objects.filter(cerrado=False).order_by('-inicio')
    periodos_cerrados = PeriodoContable.objects.filter(cerrado=True).order_by('-inicio')
    return render(request, 'periodos.html', {
        'periodos_abiertos': periodos_abiertos,
        'periodos_cerrados': periodos_cerrados,
    })

def crear_periodo_view(request):

    if PeriodoContable.objects.filter(cerrado=False).exists():
                messages.error(request, 'Ya existe un período contable abierto. Debes cerrarlo antes de crear uno nuevo.')
                return redirect('periodo_contable')

    if request.method == 'POST':
        form = PeriodoContableForm(request.POST)
        if form.is_valid():
            # Verificar si ya existe un período abierto
                periodo = form.save(commit=False)
                periodo.cerrado = False
                periodo.save()
                messages.success(request, 'Período contable creado correctamente.')
                return redirect('periodo_contable')
        else:
            messages.error(request, 'Hay errores en el formulario.')
    else:
        form = PeriodoContableForm()
    return render(request, 'crear_periodo.html', {'form': form})

def editar_periodo_view(request, pk):
    periodo = get_object_or_404(PeriodoContable, pk=pk)
    form = PeriodoContableForm(request.POST or None, instance=periodo)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Período actualizado correctamente.')
        return redirect('periodo_contable')
    return render(request, 'editar_periodo.html', {'form': form, 'periodo': periodo})

def eliminar_periodo_view(request, pk):
    periodo = get_object_or_404(PeriodoContable, pk=pk)
    if request.method == 'POST':
        periodo.delete()
        messages.success(request, f'Período "{periodo.nombre}" eliminado.')
        return redirect('periodo_contable')
    return render(request, 'eliminar_periodo.html', {'periodo': periodo})

def cerrar_periodo_view(request, pk):
    periodo = get_object_or_404(PeriodoContable, pk=pk)

    if periodo.cerrado:
        messages.info(request, f"El período {periodo.nombre} ya estaba cerrado.")
    else:
        periodo.cerrado = True
        periodo.save()
        messages.success(request, f"✅ El período {periodo.nombre} se ha cerrado correctamente.")

    return redirect('periodo_contable')