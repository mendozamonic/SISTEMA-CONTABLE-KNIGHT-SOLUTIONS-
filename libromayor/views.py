from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import Sum,F
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import AsientoContableForm, DetalleAsientoFormSet, PeriodoContableForm
from .models import AsientoContable, DetalleAsiento, Cuenta, PeriodoContable, SaldoCuenta


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



def cerrar_periodo_view(request, pk):

    periodo = get_object_or_404(PeriodoContable, pk=pk)

    if periodo.cerrado:
        messages.warning(request, f"⚠️ El período '{periodo.nombre}' ya está cerrado.")
        return redirect("periodos_contables")

    def c(codigo):
        return Cuenta.objects.get(codigo=codigo)

    TC = Cuenta.TipoCuenta  # alias para leer mejor

    # --- helper para sumar movimientos por tipo de cuenta ---
    def suma_por_tipo(tipo):
        agg = DetalleAsiento.objects.filter(asiento__periodo=periodo, cuenta__tipo_cuenta=tipo) \
            .aggregate(debe=Sum("debe"), haber=Sum("haber"))
        debe = agg["debe"] or Decimal("0.00")
        haber = agg["haber"] or Decimal("0.00")
        return debe, haber

    # Ejecutamos todo en una transacción para evitar inconsistencias parciales
    with transaction.atomic():
        # === 1️⃣ Calcular utilidad ===
        debe_ing, haber_ing = suma_por_tipo(TC.INGRESO)
        ingresos = (haber_ing - debe_ing)

        debe_cos, haber_cos = suma_por_tipo(TC.COSTO)
        costos = (debe_cos - haber_cos)
        debe_gas, haber_gas = suma_por_tipo(TC.GASTO)
        gastos = (debe_gas - haber_gas)

        utilidad = (ingresos - (costos + gastos)) or Decimal("0.00")
        print(f"💰 Utilidad neta del período: {utilidad:.2f}")

        # === 2️⃣ Crear asiento de cierre (cerrar cuentas de resultado) ===
        detalles_cierre = []
        try:
            cuenta_utilidad = c("3.2.01.")
        except Cuenta.DoesNotExist:
            cuenta_utilidad = None
            print("⚠️ No se encontró cuenta '3.2.01.' (UTILIDAD DEL EJERCICIO). Ajusta el código si es distinto.")

        cuentas_resultado = Cuenta.objects.filter(tipo_cuenta__in=[TC.INGRESO, TC.COSTO, TC.GASTO], es_imputable=True)
        for cuenta in cuentas_resultado:
            movs = DetalleAsiento.objects.filter(asiento__periodo=periodo, cuenta=cuenta) \
                .aggregate(debe=Sum("debe"), haber=Sum("haber"))
            debe = movs["debe"] or Decimal("0.00")
            haber = movs["haber"] or Decimal("0.00")

            if cuenta.tipo_cuenta == TC.INGRESO:
                # ingresos: saldo normal en el haber
                saldo = haber - debe
                if saldo > 0:
                    detalles_cierre.append(DetalleAsiento(asiento=None, cuenta=cuenta, debe=saldo))
            else:
                # costos y gastos: saldo normal en el debe
                saldo = debe - haber
                if saldo > 0:
                    detalles_cierre.append(DetalleAsiento(asiento=None, cuenta=cuenta, haber=saldo))

        if cuenta_utilidad:
            if utilidad > 0:
                detalles_cierre.append(DetalleAsiento(asiento=None, cuenta=cuenta_utilidad, haber=utilidad))
            elif utilidad < 0:
                detalles_cierre.append(DetalleAsiento(asiento=None, cuenta=cuenta_utilidad, debe=abs(utilidad)))

        asiento_cierre = None
        if detalles_cierre:
            asiento_cierre = AsientoContable.objects.create(
                periodo=periodo,
                fecha=periodo.fin,
                concepto="Cierre de cuentas de resultado y determinación de utilidad del ejercicio",
                tipo="CIERRE"
            )
            for d in detalles_cierre:
                d.asiento = asiento_cierre
            DetalleAsiento.objects.bulk_create(detalles_cierre)
        print("🧾 Cuentas de resultado cerradas y utilidad registrada (si hubo).")

        # === 3️⃣ Transferir utilidad a utilidades acumuladas (si aplica) ===
        try:
            cuenta_acumulada = c("3.2.02.")
        except Cuenta.DoesNotExist:
            cuenta_acumulada = None
            print("⚠️ No se encontró cuenta '3.2.02.' (UTILIDADES ACUMULADAS). Ajusta el código si es distinto.")

        if utilidad != Decimal("0.00") and cuenta_utilidad and cuenta_acumulada:
            asiento_traslado = AsientoContable.objects.create(
                periodo=periodo,
                fecha=periodo.fin,
                concepto="Traspaso de utilidad del ejercicio a utilidades acumuladas",
                tipo="CIERRE"
            )
            if utilidad > 0:
                # utilidad positiva: debitar cuenta de resultados, acreditar utilidades acumuladas
                DetalleAsiento.objects.bulk_create([
                    DetalleAsiento(asiento=asiento_traslado, cuenta=cuenta_utilidad, debe=utilidad),
                    DetalleAsiento(asiento=asiento_traslado, cuenta=cuenta_acumulada, haber=utilidad),
                ])
            else:
                # pérdida: debitar utilidades acumuladas, acreditar cuenta de resultados
                amt = abs(utilidad)
                DetalleAsiento.objects.bulk_create([
                    DetalleAsiento(asiento=asiento_traslado, cuenta=cuenta_acumulada, debe=amt),
                    DetalleAsiento(asiento=asiento_traslado, cuenta=cuenta_utilidad, haber=amt),
                ])
            print("🔄 Utilidad del ejercicio trasladada a utilidades acumuladas.")

        # === 4️⃣ Recalcular saldos finales (corrigiendo por normalidad de la cuenta) ===
        for cuenta in Cuenta.objects.filter(es_imputable=True):
            movs = DetalleAsiento.objects.filter(asiento__periodo=periodo, cuenta=cuenta) \
                .aggregate(debe_total=Sum("debe"), haber_total=Sum("haber"))
            debe_mov = movs["debe_total"] or Decimal("0.00")
            haber_mov = movs["haber_total"] or Decimal("0.00")

            # obtener saldo inicial (si existe) para este periodo antes de recalcular
            saldo_prev = SaldoCuenta.objects.filter(cuenta=cuenta, periodo=periodo).first()
            init_debe = saldo_prev.saldo_inicial_debe if saldo_prev else Decimal("0.00")
            init_haber = saldo_prev.saldo_inicial_haber if saldo_prev else Decimal("0.00")

            # Determinar si la cuenta es 'normalmente acreedora' o 'normalmente deudora'
            try:
                normal_acreedor = cuenta.tipo_cuenta in (TC.PASIVO, TC.PATRIMONIO, TC.INGRESO)
            except Exception:
                normal_acreedor = False

            if normal_acreedor:
                # para cuentas acreedoras (pasivo/patrimonio/ingreso): net = haber - debe
                start_net = (init_haber - init_debe)
                mov_net = (haber_mov - debe_mov)
                total_net = start_net + mov_net

                if total_net >= Decimal("0.00"):
                    saldo_final_acreedor = total_net
                    saldo_final_deudor = Decimal("0.00")
                else:
                    saldo_final_acreedor = Decimal("0.00")
                    saldo_final_deudor = abs(total_net)
            else:
                # para cuentas deudoras (activo/gasto/costo): net = debe - haber
                start_net = (init_debe - init_haber)
                mov_net = (debe_mov - haber_mov)
                total_net = start_net + mov_net

                if total_net >= Decimal("0.00"):
                    saldo_final_deudor = total_net
                    saldo_final_acreedor = Decimal("0.00")
                else:
                    saldo_final_deudor = Decimal("0.00")
                    saldo_final_acreedor = abs(total_net)

            # guardamos: los totales del mes son sólo los movimientos
            SaldoCuenta.objects.update_or_create(
                cuenta=cuenta, periodo=periodo,
                defaults={
                    "total_debe_mes": debe_mov,
                    "total_haber_mes": haber_mov,
                    "saldo_inicial_debe": init_debe,
                    "saldo_inicial_haber": init_haber,
                    "saldo_final_deudor": saldo_final_deudor,
                    "saldo_final_acreedor": saldo_final_acreedor,
                },
            )

        periodo.cerrado = True
        periodo.save(update_fields=["cerrado"])
        print(f"✅ Período {periodo.nombre} cerrado correctamente.")

        # === 5️⃣ Crear nuevo período (mes siguiente) ===
        nuevo_inicio = periodo.fin + timedelta(days=1)
        # cálculo estándar para fin de mes del nuevo periodo
        nuevo_fin = (nuevo_inicio.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        periodo_nuevo, _ = PeriodoContable.objects.get_or_create(
            nombre=f"{nuevo_inicio.strftime('%B').capitalize()} {nuevo_inicio.year}",
            inicio=nuevo_inicio,
            fin=nuevo_fin,
            defaults={"cerrado": False}
        )

        # === 6️⃣ Pasar saldos iniciales al nuevo periodo (usar saldos finales ya calculados) ===
        for saldo_ant in SaldoCuenta.objects.filter(periodo=periodo):
            init_debe = saldo_ant.saldo_final_deudor or Decimal("0.00")
            init_haber = saldo_ant.saldo_final_acreedor or Decimal("0.00")

            # Si la cuenta es del tipo PATRIMONIO o su código comienza por '3.1' (capital),
            # aseguramos que el saldo inicial quede en la columna HABER.
            asignar_por_codigo = False
            try:
                codigo = (saldo_ant.cuenta.codigo or "").strip()
                if codigo.startswith("3.1.01.") or codigo.startswith("3.1."):
                    asignar_por_codigo = True
            except Exception:
                codigo = ""

            if asignar_por_codigo or saldo_ant.cuenta.tipo_cuenta == TC.PATRIMONIO:
                # Para patrimonio dejamos init_debe a 0 y el init_haber con el valor acreedor
                # Si el valor está actualmente en init_debe (porque el final quedó en deudor), invertimos.
                if init_debe != Decimal("0.00") and init_haber == Decimal("0.00"):
                    # convertir el deudor a haber (signo) para patrimonio: poner 0 en debe y mover a haber
                    init_haber = init_debe
                    init_debe = Decimal("0.00")

            SaldoCuenta.objects.update_or_create(
                cuenta=saldo_ant.cuenta,
                periodo=periodo_nuevo,
                defaults={
                    "saldo_inicial_debe": init_debe,
                    "saldo_inicial_haber": init_haber,
                    # los totales del mes nuevo empiezan en cero
                    "total_debe_mes": Decimal("0.00"),
                    "total_haber_mes": Decimal("0.00"),
                    # y los saldos finales se inicializan igual al saldo inicial
                    "saldo_final_deudor": init_debe,
                    "saldo_final_acreedor": init_haber,
                },
            )

        # --- Prevención: si alguna cuenta quedó con final=0 en el nuevo periodo pero tiene inicial != 0, copiar inicial -> final ---
        qs_fix = SaldoCuenta.objects.filter(
            periodo=periodo_nuevo,
            saldo_final_deudor=Decimal("0.00"),
            saldo_final_acreedor=Decimal("0.00")
        ).exclude(
            saldo_inicial_debe=Decimal("0.00"),
            saldo_inicial_haber=Decimal("0.00")
        )

        if qs_fix.exists():
            cnt = qs_fix.update(
                saldo_final_deudor=F("saldo_inicial_debe"),
                saldo_final_acreedor=F("saldo_inicial_haber")
            )
            print(f"🔧 Prevención aplicada: {cnt} saldos del nuevo período actualizados (final <- inicial).")

    messages.success(request, f"🎯 Período '{periodo.nombre}' cerrado. Nuevo período '{periodo_nuevo.nombre}' creado.")
    return redirect("periodo_contable")
