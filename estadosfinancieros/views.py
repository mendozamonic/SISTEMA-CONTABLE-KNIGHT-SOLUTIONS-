from decimal import ROUND_HALF_UP, Decimal
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from libromayor.models import PeriodoContable, DetalleAsiento, SaldoCuenta, Cuenta
from collections import OrderedDict



# --------------------------------------------------------------------
# 📘 LIBRO MAYOR
# --------------------------------------------------------------------
def libro_mayor_view(request):
    periodos = PeriodoContable.objects.all().order_by('-inicio')
    periodo_id = request.GET.get("periodo_id")

    cuentas_mayor = {}
    total_global = {'debe': 0, 'haber': 0, 'saldo_inicial': 0, 'saldo_final': 0}

    if periodo_id:
        periodo = get_object_or_404(PeriodoContable, pk=periodo_id)
        periodo_anterior = PeriodoContable.objects.filter(fin__lt=periodo.inicio).order_by('-fin').first()

        detalles = (
            DetalleAsiento.objects
            .filter(asiento__periodo=periodo)
            .values('cuenta__id', 'cuenta__codigo', 'cuenta__nombre', 'cuenta__tipo_cuenta')
            .annotate(total_debe=Sum('debe'), total_haber=Sum('haber'))
            .order_by('cuenta__codigo')
        )

        saldos_iniciales = {
            s.cuenta.id: s.saldo_final_deudor - s.saldo_final_acreedor # type: ignore
            for s in SaldoCuenta.objects.filter(periodo=periodo_anterior)
        } if periodo_anterior else {}

        for d in detalles:
            cuenta_id = d['cuenta__id']
            tipo = dict(Cuenta.TipoCuenta.choices).get(d['cuenta__tipo_cuenta'], 'Sin Clasificar')
            debe = d['total_debe'] or Decimal('0.00')
            haber = d['total_haber'] or Decimal('0.00')
            saldo_inicial = saldos_iniciales.get(cuenta_id, Decimal('0.00'))
            saldo_final = saldo_inicial + debe - haber

            cuentas_mayor.setdefault(tipo, []).append({
                'codigo': d['cuenta__codigo'],
                'nombre': d['cuenta__nombre'],
                'saldo_inicial': saldo_inicial,
                'debe': debe,
                'haber': haber,
                'saldo_final': saldo_final,
                'saldo_deudor': saldo_final if saldo_final > 0 else Decimal('0.00'),
                'saldo_acreedor': abs(saldo_final) if saldo_final < 0 else Decimal('0.00'),
            })

        total_global = {
            'debe': sum(c['debe'] for lista in cuentas_mayor.values() for c in lista),
            'haber': sum(c['haber'] for lista in cuentas_mayor.values() for c in lista),
            'saldo_inicial': sum(c['saldo_inicial'] for lista in cuentas_mayor.values() for c in lista),
            'saldo_final': sum(c['saldo_final'] for lista in cuentas_mayor.values() for c in lista),
        }

    context = {
        'periodos': periodos,
        'periodo_id': periodo_id,
        'cuentas_mayor': cuentas_mayor,
        'total_global': total_global,
    }
    return render(request, 'libro_mayor.html', context)



# --------------------------------------------------------------------
# 📕 CAMBIO PATRIMONIAL (después del cierre)
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# 📗 ESTADO DE CAMBIOS EN EL PATRIMONIO (solo períodos cerrados)
# --------------------------------------------------------------------


def cambio_patrimonial_view(request):
    periodos = PeriodoContable.objects.filter(cerrado=True).order_by('-inicio')
    periodo_id = request.GET.get("periodo_id")

    # Definir grupos patrimoniales (códigos de cuenta base)
    grupos = OrderedDict({
        "CAPITAL SOCIAL": {"prefix": ["3.1.01."], "color": "#7b1c1c"},
        "UTILIDAD DEL PRESENTE EJERCICIO": {"prefix": ["3.2.01."], "color": "#a03a3a"},
        "UTILIDADES ACUMULADAS": {"prefix": ["3.2.02."], "color": "#b33e3e"},
    })

    movimientos = []
    total_debe = total_haber = Decimal("0.00")

    if periodo_id:
        periodo = get_object_or_404(PeriodoContable, pk=periodo_id, cerrado=True)
        saldos = (
            SaldoCuenta.objects.filter(periodo=periodo, cuenta__tipo_cuenta="PAT")
            .select_related("cuenta")
            .order_by("cuenta__codigo")
        )

        for grupo, info in grupos.items():
            color = info["color"]
            prefijos = info["prefix"]
            cuentas = [
                s for s in saldos if any(s.cuenta.codigo.startswith(p) for p in prefijos)
            ]

            if not cuentas:
                cuentas = []

            movimientos.append({
                "grupo": grupo,
                "color": color,
                "cuentas": cuentas,
            })

            for s in cuentas:
                total_debe += s.saldo_final_deudor
                total_haber += s.saldo_final_acreedor

    total = total_haber - total_debe

    context = {
        "periodos": periodos,
        "periodo_id": periodo_id,
        "movimientos": movimientos,
        "total_debe": total_debe,
        "total_haber": total_haber,
        "total": total,
    }
    return render(request, "cambio_patrimonial.html", context)


# --------------------------------------------------------------------
# 📒 BALANCE GENERAL 
# --------------------------------------------------------------------


def balance_general_view(request):
    periodos = PeriodoContable.objects.all().order_by('-inicio')
    periodo_id = request.GET.get("periodo_id")

    cuentas_procesadas = []
    total_debe = total_haber = Decimal('0.00')
    diferencia = Decimal('0.00')
    balance_ok = None

    if periodo_id:
        periodo = get_object_or_404(PeriodoContable, pk=periodo_id)
        cuentas = list(Cuenta.objects.order_by('codigo'))

        # 1️⃣ Saldos iniciales del período
        qs_inicial = SaldoCuenta.objects.filter(periodo=periodo).values(
            'cuenta__codigo'
        ).annotate(
            total_debe=Sum('saldo_inicial_debe'),
            total_haber=Sum('saldo_inicial_haber')
        )

        # 2️⃣ Movimientos del período (excluyendo los de cierre)
        qs_mov = DetalleAsiento.objects.filter(
            asiento__periodo=periodo
        ).exclude(asiento__tipo='CIERRE').values(
            'cuenta__codigo'
        ).annotate(
            total_debe=Sum('debe'),
            total_haber=Sum('haber')
        )

        # 3️⃣ Convertir ambos en diccionarios
        saldo_dict_inicial = {
            s['cuenta__codigo']: {
                'debe': s['total_debe'] or Decimal('0.00'),
                'haber': s['total_haber'] or Decimal('0.00'),
            }
            for s in qs_inicial
        }

        saldo_dict_mov = {
            s['cuenta__codigo']: {
                'debe': s['total_debe'] or Decimal('0.00'),
                'haber': s['total_haber'] or Decimal('0.00'),
            }
            for s in qs_mov
        }

        # 4️⃣ Combinar ambos: saldos iniciales + movimientos
        saldo_dict = {}
        for codigo in set(list(saldo_dict_inicial.keys()) + list(saldo_dict_mov.keys())):
            si = saldo_dict_inicial.get(codigo, {'debe': Decimal('0.00'), 'haber': Decimal('0.00')})
            sm = saldo_dict_mov.get(codigo, {'debe': Decimal('0.00'), 'haber': Decimal('0.00')})
            saldo_dict[codigo] = {
                'debe': si['debe'] + sm['debe'],
                'haber': si['haber'] + sm['haber'],
            }

        # =============================
        # RENDERIZAR LA TABLA
        # =============================
        for cuenta in cuentas:
            nivel = cuenta.codigo.count('.')
            padding_px = nivel * 15
            es_grupo = not cuenta.es_imputable

            debe = saldo_dict.get(cuenta.codigo, {}).get('debe', Decimal('0.00'))
            haber = saldo_dict.get(cuenta.codigo, {}).get('haber', Decimal('0.00'))

            cuentas_procesadas.append({
                'cuenta': cuenta,
                'nivel': nivel,
                'padding': padding_px,
                'es_grupo': es_grupo,
                'debe': debe,
                'haber': haber,
            })

            total_debe += debe
            total_haber += haber

        # ✅ Verificar balance
        diferencia = (total_debe - total_haber).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        balance_ok = diferencia == Decimal('0.00')

    context = {
        'periodos': periodos,
        'periodo_id': periodo_id,
        'cuentas_procesadas': cuentas_procesadas,
        'total_debe': total_debe,
        'total_haber': total_haber,
        'diferencia': diferencia,
        'balance_ok': balance_ok,
    }
    return render(request, 'balance_general.html', context)





# --------------------------------------------------------------------
# 📙 ESTADO DE RESULTADOS (antes del cierre)
# --------------------------------------------------------------------




def estado_resultados_view(request):
    periodos = PeriodoContable.objects.all().order_by('-inicio')
    periodo_id = request.GET.get("periodo_id")

    ventas = costo_ventas = gastos_admin = otros_prod = otros_gastos = Decimal('0.00')
    utilidad_bruta = utilidad_operacion = utilidad_antes_imp = utilidad_neta = Decimal('0.00')
    impuesto = Decimal('0.00')

    if periodo_id:
        periodo = get_object_or_404(PeriodoContable, pk=periodo_id)
        detalles = DetalleAsiento.objects.filter(asiento__periodo=periodo).select_related('cuenta')

        ventas = detalles.filter(cuenta__tipo_cuenta='ING').aggregate(total=Sum('haber'))['total'] or Decimal('0.00')
        costo_ventas = detalles.filter(cuenta__tipo_cuenta='COS').aggregate(total=Sum('debe'))['total'] or Decimal('0.00')
        gastos_admin = detalles.filter(cuenta__tipo_cuenta='GAS').aggregate(total=Sum('debe'))['total'] or Decimal('0.00')

        # Cálculos contables
        utilidad_bruta = ventas - costo_ventas
        utilidad_operacion = utilidad_bruta - gastos_admin
        otros_prod = Decimal('0.00')
        otros_gastos = Decimal('0.00')
        utilidad_antes_imp = utilidad_operacion + otros_prod - otros_gastos
        impuesto = utilidad_antes_imp * Decimal('0.30') if utilidad_antes_imp > 0 else Decimal('0.00')
        utilidad_neta = utilidad_antes_imp - impuesto

    context = {
        'periodos': periodos,
        'periodo_id': periodo_id,
        'ventas': ventas,
        'costo_ventas': costo_ventas,
        'gastos_admin': gastos_admin,
        'otros_prod': otros_prod,
        'otros_gastos': otros_gastos,
        'utilidad_bruta': utilidad_bruta,
        'utilidad_operacion': utilidad_operacion,
        'utilidad_antes_imp': utilidad_antes_imp,
        'impuesto': impuesto,
        'utilidad_neta': utilidad_neta,
    }
    return render(request, 'estado_resultados.html', context)
