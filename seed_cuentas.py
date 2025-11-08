# seed_cuentas.py  —  Catálogo de cuentas actualizado (Knight Solutions S.A. de C.V.)

import os
import django
import sys
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SIC.settings')
django.setup()

from libromayor.models import Cuenta

TIPO_MAP = {
    'Activo': Cuenta.TipoCuenta.ACTIVO,
    'Pasivo': Cuenta.TipoCuenta.PASIVO,
    'Patrimonio': Cuenta.TipoCuenta.PATRIMONIO,
    'Ingreso': Cuenta.TipoCuenta.INGRESO,
    'Gasto': Cuenta.TipoCuenta.GASTO,
    'Costo': Cuenta.TipoCuenta.COSTO,
}

cuentas_data = [
    # ---------------- ACTIVO ----------------
    {'codigo': '1.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'ACTIVO', 'es_imputable': False},
    {'codigo': '1.1.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'ACTIVO CORRIENTE', 'es_imputable': False},
    {'codigo': '1.1.01.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'CAJA Y BANCOS', 'es_imputable': False},
    {'codigo': '1.1.01.01.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'CAJA GENERAL', 'es_imputable': True},
    {'codigo': '1.1.01.02.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'BANCOS', 'es_imputable': True},
    {'codigo': '1.1.02.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'CUENTAS POR COBRAR', 'es_imputable': False},
    {'codigo': '1.1.02.01.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'CLIENTES', 'es_imputable': True},
    {'codigo': '1.1.02.02.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'ESTIMACIÓN CUENTAS INCOBRABLES (-)', 'es_imputable': True},
    {'codigo': '1.1.03.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'IVA CRÉDITO FISCAL', 'es_imputable': True},
    {'codigo': '1.1.04.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'INVENTARIO DE PROYECTOS EN PROCESO', 'es_imputable': True},
    {'codigo': '1.1.05.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'INSUMOS DE OFICINA', 'es_imputable': True},  # ✅ nuevo activo
    {'codigo': '1.2.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'ACTIVO NO CORRIENTE', 'es_imputable': False},
    {'codigo': '1.2.01.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'MOBILIARIO Y EQUIPO', 'es_imputable': True},
    {'codigo': '1.2.02.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'EQUIPO INFORMÁTICO', 'es_imputable': True},
    {'codigo': '1.2.03.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'DEPRECIACIÓN ACUMULADA', 'es_imputable': False},
    {'codigo': '1.2.03.01.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'DEPR. ACUM. MOBILIARIO Y EQUIPO (-)', 'es_imputable': True},
    {'codigo': '1.2.03.02.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'DEPR. ACUM. EQUIPO INFORMÁTICO (-)', 'es_imputable': True},

    # ---------------- PASIVO ----------------
    {'codigo': '2.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'PASIVO', 'es_imputable': False},
    {'codigo': '2.1.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'PASIVO CORRIENTE', 'es_imputable': False},
    {'codigo': '2.1.01.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'CUENTAS POR PAGAR', 'es_imputable': False},
    {'codigo': '2.1.01.01.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'PROVEEDORES LOCALES', 'es_imputable': True},
    {'codigo': '2.1.01.02.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'SERVICIOS DE TERCEROS', 'es_imputable': True},
    {'codigo': '2.1.02.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'IVA DÉBITO FISCAL', 'es_imputable': True},
    {'codigo': '2.1.03.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'IMPUESTO SOBRE LA RENTA POR PAGAR', 'es_imputable': True},
    {'codigo': '2.1.04.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'ANTICIPOS DE CLIENTES', 'es_imputable': True},
    {'codigo': '2.1.05.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'NÓMINA POR PAGAR', 'es_imputable': False},
    {'codigo': '2.1.05.01.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'SUELDOS POR PAGAR', 'es_imputable': True},
    {'codigo': '2.1.05.02.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'COTIZACIONES AFP POR PAGAR', 'es_imputable': True},
    {'codigo': '2.1.05.03.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'COTIZACIONES ISSS POR PAGAR', 'es_imputable': True},
    {'codigo': '2.1.05.04.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'PROVISIÓN AGUINALDO', 'es_imputable': True},
    {'codigo': '2.1.05.05.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'PROVISIÓN VACACIONES', 'es_imputable': True},

    # ---------------- PATRIMONIO ----------------
    {'codigo': '3.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'PATRIMONIO', 'es_imputable': False},
    {'codigo': '3.1.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'CAPITAL', 'es_imputable': False},
    {'codigo': '3.1.01.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'CAPITAL SOCIAL', 'es_imputable': True},
    {'codigo': '3.2.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'UTILIDADES', 'es_imputable': False},
    {'codigo': '3.2.01.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'UTILIDAD DEL EJERCICIO', 'es_imputable': True},
    {'codigo': '3.2.02.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'UTILIDADES ACUMULADAS', 'es_imputable': True},

    # ---------------- COSTOS Y GASTOS ----------------
    {'codigo': '4.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'COSTOS Y GASTOS DE OPERACIÓN', 'es_imputable': False},
    {'codigo': '4.1.', 'tipoDeCuenta': 'Costo', 'nombreDeCuenta': 'COSTO DE VENTA', 'es_imputable': False},
    {'codigo': '4.1.01.', 'tipoDeCuenta': 'Costo', 'nombreDeCuenta': 'COSTO DE VENTA', 'es_imputable': True},
    {'codigo': '4.2.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS DE OPERACIÓN', 'es_imputable': False},
    {'codigo': '4.2.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS DE ADMINISTRACIÓN', 'es_imputable': False},
    {'codigo': '4.2.01.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SALARIOS PERSONAL ADMIN.', 'es_imputable': True},
    {'codigo': '4.2.01.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'PRESTACIONES PERSONAL ADMIN.', 'es_imputable': True},
    {'codigo': '4.2.01.03.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'ALQUILER LOCAL', 'es_imputable': True},
    {'codigo': '4.2.01.04.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SERVICIOS BÁSICOS', 'es_imputable': True},
    {'codigo': '4.2.01.05.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SERVICIOS DE TERCEROS', 'es_imputable': True},
    {'codigo': '4.2.01.06.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'DEPRECIACIÓN MOBILIARIO Y EQUIPO', 'es_imputable': True},
    {'codigo': '4.2.01.07.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'INSUMOS DE OFICINA CONSUMIDOS', 'es_imputable': True},  # ✅ nuevo gasto
    {'codigo': '4.2.01.08.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'MANTENIMIENTO Y REPARACIONES', 'es_imputable': True},
    {'codigo': '4.2.01.09.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS VARIOS', 'es_imputable': True},
    {'codigo': '4.2.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS DE MARKETING', 'es_imputable': False},
    {'codigo': '4.2.02.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SALARIOS PERSONAL MARKETING', 'es_imputable': True},
    {'codigo': '4.2.02.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'PRESTACIONES PERSONAL MARKETING', 'es_imputable': True},
    {'codigo': '4.2.02.03.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'PUBLICIDAD Y PROMOCIÓN', 'es_imputable': True},
    {'codigo': '4.2.03.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTO PERSONAL TÉCNICO  ', 'es_imputable': False},
    {'codigo': '4.2.03.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SALARIOS PERSONAL  ', 'es_imputable': True},
    {'codigo': '4.2.03.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'PRESTACIONES PERSONAL ', 'es_imputable': True},
    {'codigo': '4.2.04.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS DE TECNOLOGÍA (NO ASIGNADOS)', 'es_imputable': False},
    {'codigo': '4.2.04.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'LICENCIAS Y SUSCRIPCIONES', 'es_imputable': True},
    {'codigo': '4.2.04.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'DEPRECIACIÓN EQUIPO INFORMÁTICO (USO GENERAL)', 'es_imputable': True},
    {'codigo': '4.2.04.03.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'MANTENIMIENTO EQUIPO INFORMÁTICO', 'es_imputable': True},

    # ---------------- INGRESOS ----------------
    {'codigo': '5.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'INGRESOS', 'es_imputable': False},
    {'codigo': '5.1.01.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'INGRESOS POR PROYECTO DE SOFTWARE', 'es_imputable': True},
    {'codigo': '5.1.02.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'OTROS INGRESOS', 'es_imputable': True},
    {'codigo': '5.1.03.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'GANANCIA EN VENTA DE ACTIVOS FIJOS', 'es_imputable': True},
    {'codigo': '5.1.04.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'PRODUCTOS FINANCIEROS', 'es_imputable': True},
]


def cargar_cuentas():
    print("📘 Cargando catálogo actualizado de Knight Solutions S.A. de C.V.…")
    creadas, actualizadas = 0, 0

    for data in cuentas_data:
        tipo_destino = TIPO_MAP.get(data['tipoDeCuenta'])
        cuenta, creada = Cuenta.objects.update_or_create(
            codigo=data['codigo'],
            defaults={
                'nombre': data['nombreDeCuenta'],
                'tipo_cuenta': tipo_destino,
                'es_imputable': data['es_imputable'],
            },
        )
        if creada:
            creadas += 1
        else:
            actualizadas += 1

    print(f"✅ Catálogo cargado correctamente | Nuevas {creadas} | Actualizadas {actualizadas} | Total {len(cuentas_data)}")


if __name__ == "__main__":
    cargar_cuentas()
