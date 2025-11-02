import os
import django
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SIC.settings')
django.setup()

from libromayor.models import (
    PeriodoContable, Cuenta, AsientoContable, DetalleAsiento, SaldoCuenta
)


def run():
    # === CREAR PERÍODO CONTABLE ===
    periodo, _ = PeriodoContable.objects.get_or_create(
        nombre="Noviembre 2025",
        inicio=date(2025, 11, 1),
        fin=date(2025, 11, 30),
        cerrado=False
    )

    def c(codigo):
        return Cuenta.objects.get(codigo=codigo)

    # === 1️⃣ Aporte inicial de capital (126,000) ===
    asiento1 = AsientoContable.objects.create(
        periodo=periodo, fecha=date(2025, 11, 1),
        concepto="Aporte inicial de socios a la cuenta bancaria (Capital Social 126,000)",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento1, cuenta=c("1.1.01.01."), debe=Decimal("16000.00")),  # Bancos
        DetalleAsiento(asiento=asiento1, cuenta=c("1.1.01.02."), debe=Decimal("110000.00")),  # Bancos
        DetalleAsiento(asiento=asiento1, cuenta=c("3.1.01."), haber=Decimal("126000.00")),    # Capital social
    ])

    # === 2️⃣ Compra de mobiliario y equipo (pago desde BANCOS) ===
    asiento2 = AsientoContable.objects.create(
        periodo=periodo, fecha=date(2025, 11, 3),
        concepto="Compra de mobiliario y equipo de oficina",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento2, cuenta=c("1.2.01."), debe=Decimal("7575.00")),   # Mobiliario
        DetalleAsiento(asiento=asiento2, cuenta=c("1.2.02."), debe=Decimal("23750.00")),  # Equipo informático
        DetalleAsiento(asiento=asiento2, cuenta=c("1.1.01.02."), haber=Decimal("31325.00")),  # Bancos (NO caja)
    ])

    # === 3️⃣ Anticipo del cliente (30%) ===
    asiento3 = AsientoContable.objects.create(
        periodo=periodo, fecha=date(2025, 11, 5),
        concepto="Anticipo del cliente para proyecto de software (30%)",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento3, cuenta=c("1.1.01.02."), debe=Decimal("3600.00")),  # Bancos
        DetalleAsiento(asiento=asiento3, cuenta=c("2.1.04."), haber=Decimal("3600.00")),    # Anticipos de clientes
    ])

    # === 4️⃣ Compra de insumos de oficina (sin inventario de proyectos) ===
    asiento4 = AsientoContable.objects.create(
        periodo=periodo, fecha=date(2025, 11, 6),
        concepto="Compra de insumos de oficina",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento4, cuenta=c("1.1.05."), debe=Decimal("350.00")),
        DetalleAsiento(asiento=asiento4, cuenta=c("1.1.01.02."), haber=Decimal("350.00")),
    ])

    # === 5️⃣ Gastos administrativos (alquiler, mantenimiento, limpieza) ===
    asiento5 = AsientoContable.objects.create(
        periodo=periodo, fecha=date(2025, 11, 7),
        concepto="Pago de alquiler, mantenimiento y limpieza",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento5, cuenta=c("4.2.01.03."), debe=Decimal("1200.00")),  # Alquiler
        DetalleAsiento(asiento=asiento5, cuenta=c("4.2.01.08."), debe=Decimal("400.00")),   # Mantenimiento
        DetalleAsiento(asiento=asiento5, cuenta=c("4.2.01.09."), debe=Decimal("400.00")),   # Limpieza
        DetalleAsiento(asiento=asiento5, cuenta=c("1.1.01.02."), haber=Decimal("2000.00")), # Bancos
    ])

    # === 6️⃣ Venta del proyecto (facturación total 12,000 + IVA) ===
    asiento6 = AsientoContable.objects.create(
        periodo=periodo, fecha=date(2025, 11, 15),
        concepto="Venta del proyecto de software (factura total)",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento6, cuenta=c("1.1.02.01."), debe=Decimal("13560.00")),  # Clientes (CxC con IVA)
        DetalleAsiento(asiento=asiento6, cuenta=c("5.1.01."), haber=Decimal("12000.00")),    # Ingresos por proyecto
        DetalleAsiento(asiento=asiento6, cuenta=c("2.1.02."), haber=Decimal("1560.00")),     # IVA Débito Fiscal
    ])

    # === 7️⃣ Compensación del anticipo contra CxC ===
    asiento7 = AsientoContable.objects.create(
        periodo=periodo, fecha=date(2025, 11, 16),
        concepto="Compensación del anticipo del cliente contra la cuenta por cobrar",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento7, cuenta=c("2.1.04."), debe=Decimal("3600.00")),      # Baja anticipo (pasivo)
        DetalleAsiento(asiento=asiento7, cuenta=c("1.1.02.01."), haber=Decimal("3600.00")),  # Baja parcial CxC
    ])

    # === 8️⃣ Costos del proyecto (sueldos técnicos + CIF) ===
    asiento8 = AsientoContable.objects.create(
        periodo=periodo, fecha=date(2025, 11, 18),
        concepto="Registro de costos directos del proyecto (sueldos técnicos y CIF)",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento8, cuenta=c("4.1.01."), debe=Decimal("7500.00")),      # Costo de venta
        DetalleAsiento(asiento=asiento8, cuenta=c("1.1.01.02."), haber=Decimal("7500.00")),  # Bancos
    ])

    # === 9️⃣ Depreciación mensual (mobiliario y equipo) ===
    asiento9 = AsientoContable.objects.create(
        periodo=periodo, fecha=date(2025, 11, 30),
        concepto="Depreciación mensual de mobiliario y equipo informático",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento9, cuenta=c("4.2.01.06."), debe=Decimal("63.13")),    # Gasto dep. mobiliario
        DetalleAsiento(asiento=asiento9, cuenta=c("1.2.03.01."), haber=Decimal("63.13")),   # Depr. acum. mobiliario
        DetalleAsiento(asiento=asiento9, cuenta=c("4.2.04.02."), debe=Decimal("395.83")),   # Gasto dep. equipo
        DetalleAsiento(asiento=asiento9, cuenta=c("1.2.03.02."), haber=Decimal("395.83")),  # Depr. acum. equipo
    ])

    print("✅ Asientos registrados correctamente (capital 126k, anticipo y depreciación).")

    # === CALCULAR SALDOS ===
    for cuenta in Cuenta.objects.filter(es_imputable=True):
        movs = DetalleAsiento.objects.filter(asiento__periodo=periodo, cuenta=cuenta)\
            .aggregate(debe_total=Sum("debe"), haber_total=Sum("haber"))
        debe = movs["debe_total"] or Decimal("0.00")
        haber = movs["haber_total"] or Decimal("0.00")

        if cuenta.tipo_cuenta in ["ACT", "GAS", "COS"]:
            saldo = debe - haber
            saldo_deudor = max(Decimal("0.00"), saldo)
            saldo_acreedor = max(Decimal("0.00"), -saldo)
        else:
            saldo = haber - debe
            saldo_deudor = max(Decimal("0.00"), -saldo)
            saldo_acreedor = max(Decimal("0.00"), saldo)

        SaldoCuenta.objects.update_or_create(
            cuenta=cuenta, periodo=periodo,
            defaults={
                "total_debe_mes": debe,
                "total_haber_mes": haber,
                "saldo_final_deudor": saldo_deudor,
                "saldo_final_acreedor": saldo_acreedor,
            },
        )

    print("📊 Saldos calculados correctamente.")

    # === CIERRE DEL PERÍODO ===
    ingresos = DetalleAsiento.objects.filter(asiento__periodo=periodo, cuenta__tipo_cuenta='ING') \
        .aggregate(total=Sum('haber') - Sum('debe'))['total'] or Decimal('0.00')
    costos = DetalleAsiento.objects.filter(asiento__periodo=periodo, cuenta__tipo_cuenta='COS') \
        .aggregate(total=Sum('debe') - Sum('haber'))['total'] or Decimal('0.00')
    gastos = DetalleAsiento.objects.filter(asiento__periodo=periodo, cuenta__tipo_cuenta='GAS') \
        .aggregate(total=Sum('debe') - Sum('haber'))['total'] or Decimal('0.00')
    utilidad = ingresos - (costos + gastos)
    print(f"💰 Utilidad neta del período: {utilidad:.2f}")

    asiento_cierre = AsientoContable.objects.create(
        periodo=periodo, fecha=periodo.fin,
        concepto="Cierre de cuentas de resultado y determinación de utilidad del ejercicio",
        tipo="CIERRE"
    )

    detalles_cierre = []
    cuenta_utilidad = c("3.2.01.")
    # cuenta_utilidad = c("3.2.02.")


    for cuenta in Cuenta.objects.filter(tipo_cuenta__in=["ING", "COS", "GAS"], es_imputable=True):
        movs = DetalleAsiento.objects.filter(asiento__periodo=periodo, cuenta=cuenta)\
            .aggregate(debe=Sum("debe"), haber=Sum("haber"))
        debe = movs["debe"] or Decimal("0.00")
        haber = movs["haber"] or Decimal("0.00")
        saldo = debe - haber
        if saldo == 0:
            continue
        if cuenta.tipo_cuenta == "ING" and saldo < 0:
            detalles_cierre.append(DetalleAsiento(asiento=asiento_cierre, cuenta=cuenta, debe=abs(saldo)))
        elif cuenta.tipo_cuenta in ["GAS", "COS"] and saldo > 0:
            detalles_cierre.append(DetalleAsiento(asiento=asiento_cierre, cuenta=cuenta, haber=saldo))

    if utilidad > 0:
        detalles_cierre.append(DetalleAsiento(asiento=asiento_cierre, cuenta=cuenta_utilidad, haber=utilidad))
    else:
        detalles_cierre.append(DetalleAsiento(asiento=asiento_cierre, cuenta=cuenta_utilidad, debe=abs(utilidad)))

    DetalleAsiento.objects.bulk_create(detalles_cierre)
    print("🧾 Cuentas de resultado cerradas y utilidad registrada.")

    # --- Actualizar saldos finales ---
    for saldo in SaldoCuenta.objects.filter(periodo=periodo):
        cuenta = saldo.cuenta
        movs = DetalleAsiento.objects.filter(asiento__periodo=periodo, cuenta=cuenta)\
            .aggregate(debe_total=Sum("debe"), haber_total=Sum("haber"))
        debe = movs["debe_total"] or Decimal("0.00")
        haber = movs["haber_total"] or Decimal("0.00")

        if cuenta.tipo_cuenta in ["ING", "COS", "GAS"]:
            saldo.saldo_final_deudor = Decimal("0.00")
            saldo.saldo_final_acreedor = Decimal("0.00")
        else:
            if cuenta.tipo_cuenta == "ACT":
                saldo.saldo_final_deudor = max(Decimal("0.00"), debe - haber)
                saldo.saldo_final_acreedor = max(Decimal("0.00"), haber - debe)
            else:
                saldo.saldo_final_acreedor = max(Decimal("0.00"), haber - debe)
                saldo.saldo_final_deudor = max(Decimal("0.00"), debe - haber)
        saldo.save()

    periodo.cerrado = True
    periodo.save(update_fields=["cerrado"])
    print(f"✅ Período {periodo.nombre} cerrado correctamente.")

    # === NUEVO PERÍODO ===
    nuevo_inicio = periodo.fin + timedelta(days=1)
    nuevo_fin = (nuevo_inicio.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    periodo_nuevo, _ = PeriodoContable.objects.get_or_create(
        nombre=f"{nuevo_inicio.strftime('%B').capitalize()} {nuevo_inicio.year}",
        inicio=nuevo_inicio, fin=nuevo_fin, cerrado=False
    )

    # --- Pasar todos los saldos (con resultado ya en 0) ---
    for saldo_ant in SaldoCuenta.objects.filter(periodo=periodo):
        SaldoCuenta.objects.update_or_create(
            cuenta=saldo_ant.cuenta,
            periodo=periodo_nuevo,
            defaults={
                "saldo_inicial_debe": saldo_ant.saldo_final_deudor,
                "saldo_inicial_haber": saldo_ant.saldo_final_acreedor,
                "saldo_final_deudor": saldo_ant.saldo_final_deudor,
                "saldo_final_acreedor": saldo_ant.saldo_final_acreedor,
            },
        )

    print(f"📘 Nuevo período creado: {periodo_nuevo.nombre}")
    print("🎯 Cierre y apertura completados exitosamente.")


if __name__ == "__main__":
    run()
