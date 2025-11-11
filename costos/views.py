from django.shortcuts import render

# Create your views here.
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from .models import Proyecto, HorasEstimadasEmpleado
from .formsProyecto import HorasEmpleadoFormSet, ProyectoForm, HorasEstimadasEmpleadoForm
from libromayor.models import *
from django.utils import timezone
from gestion_ucp.models import EstimacionUCP as UCP  # 👈 importa el modelo
from empleados.models import Empleado
from django.http import JsonResponse
from decimal import Decimal, ROUND_HALF_UP


def lista_proyectos(request):
    cotizaciones = Proyecto.objects.filter(estado='PRE')
    proyectos = Proyecto.objects.exclude(estado='PRE')
    return render(request, 'lista_proyectos.html', {
        'cotizaciones': cotizaciones,
        'proyectos': proyectos
    })


def crear_proyecto(request):
    # 🔹 Obtener último UCP disponible
    ultimo_ucp = UCP.objects.order_by('-id').first()

    # 🔸 Verificar que haya un UCP activo
    if not ultimo_ucp or getattr(ultimo_ucp, 'usado', False):  # o .estado != 'ACTIVO' según tu modelo
        messages.warning(request, "⚠️ No hay un UCP activo disponible. Debes crear uno antes de generar un proyecto.")
        return redirect('ucp_view')

    horas_ucp = float(ultimo_ucp.horas_totales) if ultimo_ucp else 0

    # 🔹 Obtener parámetros globales
    try:
        params = ParametrosGlobales.objects.first()
        tasa_iva = float(params.porcentaje_iva) if params and params.porcentaje_iva else 0.13
        tasa_indirectos = float(params.tasa_gastos_indirectos_por_hora) if params and params.tasa_gastos_indirectos_por_hora else 0.0
    except Exception as e:
        print(f"⚠️ Error obteniendo parámetros: {e}")
        tasa_iva = 0.13
        tasa_indirectos = 0.0

    # 🔹 Procesar formulario principal y formset
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        formset = HorasEmpleadoFormSet(request.POST)  # 👈 sin prefix

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    proyecto = form.save(commit=False)
                    proyecto.estado = 'PRE'
                    proyecto.ucp = ultimo_ucp  # 👈 opcional si tu modelo Proyecto tiene FK a UCP
                    proyecto.save()

                    # Guardar los empleados
                    formset.instance = proyecto
                    formset.save()

                    # Calcular totales si aplica
                    if hasattr(proyecto, 'calcular_todo'):
                        proyecto.calcular_todo()

                    # 🔸 Marcar el UCP como usado
                    ultimo_ucp.usado = True  # o ultimo_ucp.estado = 'USADO'
                    ultimo_ucp.save()

                messages.success(request, f'✅ Proyecto "{proyecto.nombre}" creado exitosamente. El UCP fue marcado como usado.')
                return redirect('proyectos_lista')

            except Exception as e:
                print("⚠️ Error al guardar:", e)
                messages.error(request, f'❌ Error al guardar el proyecto: {e}')

        else:
            print("⚠️ Errores en ProyectoForm:", form.errors)
            print("⚠️ Errores en Formset:", formset.errors)
            messages.error(request, 'Hubo errores en el formulario. Por favor revisa los campos.')

    else:
        form = ProyectoForm()
        formset = HorasEmpleadoFormSet()  # 👈 sin prefix

    # 🔹 Renderizar plantilla
    return render(request, 'crear_proyecto.html', {
        'form': form,
        'formset': formset,
        'horas_ucp': horas_ucp,
        'tasa_iva': tasa_iva,
        'tasa_indirectos': tasa_indirectos,
    })



def obtener_costo_empleado(request, empleado_id):            
    try:
        empleado = Empleado.objects.get(id=empleado_id)
        costo = empleado.costo_real_hora_ajustado or Decimal('0.00')
        return JsonResponse({'costo_hora': float(costo)})
    except Empleado.DoesNotExist:
        return JsonResponse({'error': 'Empleado no encontrado'}, status=404)



def eliminar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    try:
        proyecto.delete()
        messages.success(request, 'Proyecto eliminado correctamente.')
    except Exception as e:
        messages.error(request, f"No se puede eliminar: {e}")
    return redirect('proyectos_lista')


@transaction.atomic
def pagar_anticipo(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)

    if proyecto.anticipo_pagado:
        messages.warning(request, "⚠️ El anticipo ya fue registrado.")
        return redirect('proyectos_lista')

    periodo = PeriodoContable.objects.filter(cerrado=False).first()
    if not periodo:
        messages.error(request, "❌ No hay un período contable abierto.")
        return redirect('proyectos_lista')

    try:
        with transaction.atomic():
            asiento = AsientoContable.objects.create(
                periodo=periodo,
                fecha=timezone.now(),
                concepto=f"Pago de anticipo del cliente {proyecto.cliente} (incluye IVA) - Proyecto '{proyecto.nombre}'",
                tipo='DIARIO',
                proyecto_relacionado=proyecto
            )

            # 🔹 Cuentas
            cuenta_bancos = get_object_or_404(Cuenta, codigo='1.1.01.02.')    # Bancos
            cuenta_clientes = get_object_or_404(Cuenta, codigo='1.1.02.01.')  # Clientes
            cuenta_iva = get_object_or_404(Cuenta, codigo='2.1.02.')          # IVA Débito Fiscal
            cuenta_ingreso = get_object_or_404(Cuenta, codigo='5.1.01.')      # Ingresos por proyecto


            # 🔹 Calcular IVA incluido en el anticipo
            params = ParametrosGlobales.objects.first()
            tasa_iva = Decimal(params.porcentaje_iva) if params and params.porcentaje_iva else Decimal('0.13')
            monto_total = proyecto.anticipo
            iva_anticipo = proyecto.precio_total_con_iva - proyecto.precio_venta
            monto_sin_iva = proyecto.precio_total_con_iva - iva_anticipo

            # 🔹 Crear partida contable
            DetalleAsiento.objects.bulk_create([
                # Anticipo recibido
                DetalleAsiento(asiento=asiento, cuenta=cuenta_bancos, debe=monto_total),
                DetalleAsiento(asiento=asiento, cuenta=cuenta_clientes, haber=monto_total),
                # Reconocimiento total del ingreso (venta completa con IVA)
                DetalleAsiento(asiento=asiento, cuenta=cuenta_clientes, debe=proyecto.precio_total_con_iva),
                DetalleAsiento(asiento=asiento, cuenta=cuenta_iva, haber=iva_anticipo),
                DetalleAsiento(asiento=asiento, cuenta=cuenta_ingreso, haber=monto_sin_iva),
            ])

            # 🔹 Actualizar proyecto
            proyecto.anticipo_pagado = True
            proyecto.estado = 'PRO'
            proyecto.save(update_fields=['anticipo_pagado', 'estado'])

            messages.success(request, f"✅ Anticipo registrado: ${monto_total:.2f} (IVA: ${iva_anticipo:.2f}, neto: ${monto_sin_iva:.2f})")
            return redirect('proyectos_lista')

    except Exception as e:
        messages.error(request, f"❌ Error al registrar el anticipo: {e}")
        return redirect('proyectos_lista')







@transaction.atomic
def pagar_completo(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)

    # ⚠️ Verificación correcta del estado
    if proyecto.estado == 'CAN':
        messages.warning(request, "⚠️ El proyecto ya fue cancelado o pagado completamente.")
        return redirect('proyectos_lista')

    # Verificar periodo contable
    periodo = PeriodoContable.objects.filter(cerrado=False).first()
    if not periodo:
        messages.error(request, "❌ No hay un período contable abierto.")
        return redirect('proyectos_lista')

    try:
        # Crear asiento contable
        asiento = AsientoContable.objects.create(
            periodo=periodo,
            fecha=timezone.now(),
            concepto=f"Pago completo y cancelación del proyecto {proyecto.nombre}",
            tipo='DIARIO',
            proyecto_relacionado=proyecto
        )

        # 🔹 Cuentas del catálogo
        cuenta_clientes = get_object_or_404(Cuenta, codigo='1.1.02.01.')  # Clientes
        cuenta_banco = get_object_or_404(Cuenta, codigo='1.1.01.02.')     # Bancos
        cuenta_caja = get_object_or_404(Cuenta, codigo='1.1.01.01.')      # Caja General

        # 🔹 Calcular pendiente de pago
        total = Decimal(proyecto.precio_total_con_iva or 0)
        anticipo = Decimal(proyecto.anticipo or 0)
        pendiente = total - anticipo

        # Mitad en caja y mitad en banco
        mitad = (pendiente / Decimal('2')).quantize(Decimal('0.01'))
        mitad2 = pendiente - mitad

        # 🔹 Registrar asiento contable
        DetalleAsiento.objects.bulk_create([
            DetalleAsiento(asiento=asiento, cuenta=cuenta_caja, debe=mitad),
            DetalleAsiento(asiento=asiento, cuenta=cuenta_banco, debe=mitad2),
            DetalleAsiento(asiento=asiento, cuenta=cuenta_clientes, haber=pendiente),
        ])

        # 🔹 Actualizar proyecto
        proyecto.completo_pagado = True  # ⚠️ ahora sí lo definimos
        proyecto.estado = 'CAN'
        proyecto.save(update_fields=['completo_pagado', 'estado'])

        messages.success(
            request,
            f"✅ Pago completo registrado (${pendiente:.2f}). "
            f"Proyecto '{proyecto.nombre}' marcado como Cancelado."
        )
        return redirect('proyectos_lista')

    except Exception as e:
        messages.error(request, f"❌ Error al registrar pago completo: {e}")
        return redirect('proyectos_lista')


def mostrar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    empleados = HorasEstimadasEmpleado.objects.filter(proyecto=proyecto)

    # 🔹 Calcular el costo total por empleado
    detalle_empleados = []
    for he in empleados:
        costo_hora = he.empleado.costo_real_hora_ajustado or 0
        subtotal = float(he.horas_estimadas) * float(costo_hora)
        detalle_empleados.append({
            'nombre': he.empleado.nombre,
            'costo_hora': float(costo_hora),
            'horas': float(he.horas_estimadas),
            'subtotal': round(subtotal, 2)
        })

    return render(request, 'mostrar_proyecto.html', {
        'proyecto': proyecto,
        'detalle_empleados': detalle_empleados
    })
