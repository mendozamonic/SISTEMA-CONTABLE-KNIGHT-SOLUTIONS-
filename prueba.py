import os
import django
from datetime import date
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SIC.settings')
django.setup()

from libromayor.models import PeriodoContable, Cuenta, AsientoContable, DetalleAsiento


def run():
    periodo = PeriodoContable.objects.get(nombre="December 2025")  # o ajusta el nombre si es otro
    c = lambda codigo: Cuenta.objects.get(codigo=codigo)

    # === 1️⃣ Cobro de anticipo del 30% del proyecto ===
    asiento1 = AsientoContable.objects.create(
        periodo=periodo,
        fecha=date(2025, 12, 1),
        concepto="Anticipo del 30% del proyecto de software",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento1, cuenta=c("1.1.01.01."), debe=Decimal("3390.00")),  # Caja general
        DetalleAsiento(asiento=asiento1, cuenta=c("2.1.04."), haber=Decimal("3390.00")),    # Anticipos de clientes
    ])

    # === 2️⃣ Cobro del saldo del proyecto (70%) vía bancos ===
    asiento2 = AsientoContable.objects.create(
        periodo=periodo,
        fecha=date(2025, 12, 2),
        concepto="Cobro del saldo restante del proyecto de software",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento2, cuenta=c("1.1.01.02."), debe=Decimal("8060.00")),   # Bancos
        DetalleAsiento(asiento=asiento2, cuenta=c("1.1.02.01."), haber=Decimal("8060.00")),  # Clientes
    ])

    # === 3️⃣ Registro de la venta total del proyecto ===
    asiento3 = AsientoContable.objects.create(
        periodo=periodo,
        fecha=date(2025, 12, 3),
        concepto="Venta total del proyecto de software",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento3, cuenta=c("1.1.02.01."), debe=Decimal("11300.00")),  # CxC
        DetalleAsiento(asiento=asiento3, cuenta=c("5.1.01."), haber=Decimal("10000.00")),    # Ingresos por proyecto
        DetalleAsiento(asiento=asiento3, cuenta=c("2.1.02."), haber=Decimal("1300.00")),     # IVA Débito Fiscal
    ])

    # === 4️⃣ Registro del costo del proyecto ===
    asiento4 = AsientoContable.objects.create(
        periodo=periodo,
        fecha=date(2025, 12, 4),
        concepto="Reconocimiento del costo de venta del proyecto",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento4, cuenta=c("4.1.01."), debe=Decimal("6000.00")),     # Costo de venta
        DetalleAsiento(asiento=asiento4, cuenta=c("1.1.01.02."), haber=Decimal("6000.00")), # Bancos
    ])

    # === 5️⃣ Registro de gastos administrativos ===
    asiento5 = AsientoContable.objects.create(
        periodo=periodo,
        fecha=date(2025, 12, 5),
        concepto="Gastos administrativos del mes",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento5, cuenta=c("4.2.01.01."), debe=Decimal("2500.00")),  # Salarios Adm.
        DetalleAsiento(asiento=asiento5, cuenta=c("4.2.01.02."), debe=Decimal("700.00")),   # Prestaciones Adm.
        DetalleAsiento(asiento=asiento5, cuenta=c("4.2.01.03."), debe=Decimal("1200.00")),  # Alquiler
        DetalleAsiento(asiento=asiento5, cuenta=c("4.2.01.04."), debe=Decimal("275.00")),   # Servicios básicos
        DetalleAsiento(asiento=asiento5, cuenta=c("1.1.01.02."), haber=Decimal("4675.00")), # Pago desde bancos
    ])

    # === 6️⃣ Registro de productos financieros (intereses ganados) ===
    asiento6 = AsientoContable.objects.create(
        periodo=periodo,
        fecha=date(2025, 12, 6),
        concepto="Intereses ganados por depósitos bancarios",
        tipo="DIARIO"
    )
    DetalleAsiento.objects.bulk_create([
        DetalleAsiento(asiento=asiento6, cuenta=c("1.1.01.02."), debe=Decimal("150.00")),   # Bancos
        DetalleAsiento(asiento=asiento6, cuenta=c("5.1.04."), haber=Decimal("150.00")),     # Productos financieros
    ])

    print("✅ Asientos de prueba creados correctamente.")


if __name__ == "__main__":
    run()
