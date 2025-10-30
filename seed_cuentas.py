import os
import django
import sys
from decimal import Decimal

# --- Configuración de Django ---
# Asegúrate de que 'SIC.settings' sea el nombre correcto de tu proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SIC.settings') 
try:
    django.setup()
except ImportError as exc:
    raise ImportError(
        "No se pudo importar Django. ¿Estás seguro de que está instalado y "
        "disponible en tu PYTHONPATH? ¿Olvidaste activar un entorno virtual?"
    ) from exc
# --- Fin de Configuración ---

# 1. Importar el modelo 'Cuenta' desde 'libromayor'
try:
    from libromayor.models import Cuenta 
except ImportError:
    print("Error: No se pudo encontrar el modelo 'Cuenta' en la app 'libromayor'.")
    print("Asegúrate de que tu app se llama 'libromayor' y el modelo 'Cuenta' existe allí.")
    sys.exit(1)


# 2. Mapeo de los tipos de cuenta (string) a los 'choices' del modelo
TIPO_MAP = {
    'Activo': Cuenta.TipoCuenta.ACTIVO,
    'Pasivo': Cuenta.TipoCuenta.PASIVO,
    'Patrimonio': Cuenta.TipoCuenta.PATRIMONIO,
    'Ingreso': Cuenta.TipoCuenta.INGRESO,
    'Gasto': Cuenta.TipoCuenta.GASTO,
    'Costo': Cuenta.TipoCuenta.COSTO,
}

# 3. Catálogo de cuentas adaptado a tu lista
#
#    *** MODIFICADO ***
#    Se agregó la llave 'es_imputable':
#    - False: Es una cuenta de grupo (no recibe asientos).
#    - True:  Es una cuenta de detalle (sí recibe asientos).
#
cuentas_data = [
    # Activos
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
    {'codigo': '1.2.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'ACTIVO NO CORRIENTE', 'es_imputable': False},
    {'codigo': '1.2.01.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'MOBILIARIO Y EQUIPO', 'es_imputable': True},
    {'codigo': '1.2.02.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'EQUIPO INFORMÁTICO', 'es_imputable': True},
    {'codigo': '1.2.03.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'DEPRECIACIÓN ACUMULADA', 'es_imputable': False},
    {'codigo': '1.2.03.01.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'DEPR. ACUM. MOBILIARIO Y EQUIPO (-)', 'es_imputable': True},
    {'codigo': '1.2.03.02.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'DEPR. ACUM. EQUIPO INFORMÁTICO (-)', 'es_imputable': True},
    
    # Pasivos
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

    # Patrimonio
    {'codigo': '3.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'PATRIMONIO', 'es_imputable': False},
    {'codigo': '3.1.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'CAPITAL', 'es_imputable': False},
    {'codigo': '3.1.01.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'CAPITAL SOCIAL', 'es_imputable': True},
    {'codigo': '3.2.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'UTILIDADES', 'es_imputable': False},
    {'codigo': '3.2.01.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'UTILIDAD DEL EJERCICIO', 'es_imputable': True},
    {'codigo': '3.2.02.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'UTILIDADES ACUMULADAS', 'es_imputable': True},

    # Costos y Gastos
    {'codigo': '4.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'COSTOS Y GASTOS DE OPERACIÓN', 'es_imputable': False},
    {'codigo': '4.1.', 'tipoDeCuenta': 'Costo', 'nombreDeCuenta': 'COSTO DE VENTA', 'es_imputable': False},
    {'codigo': '4.1.01.', 'tipoDeCuenta': 'Costo', 'nombreDeCuenta': 'COSTO DE VENTA', 'es_imputable': True}, # La imputable
    {'codigo': '4.2.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS DE OPERACIÓN', 'es_imputable': False},
    {'codigo': '4.2.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS DE ADMINISTRACIÓN', 'es_imputable': False},
    {'codigo': '4.2.01.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SALARIOS PERSONAL ADMIN.', 'es_imputable': True},
    {'codigo': '4.2.01.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'PRESTACIONES PERSONAL ADMIN.', 'es_imputable': True},
    {'codigo': '4.2.01.03.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'ALQUILER LOCAL', 'es_imputable': True},
    {'codigo': '4.2.01.04.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SERVICIOS BÁSICOS', 'es_imputable': True},
    {'codigo': '4.2.01.05.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SERVICIOS DE TERCEROS', 'es_imputable': True},
    {'codigo': '4.2.01.06.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'DEPRECIACIÓN MOBILIARIO Y EQUIPO', 'es_imputable': True},
    {'codigo': '4.2.01.07.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SUMINISTROS DE OFICINA', 'es_imputable': True},
    {'codigo': '4.2.01.08.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'MANTENIMIENTO Y REPARACIONES', 'es_imputable': True},
    {'codigo': '4.2.01.09.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS VARIOS', 'es_imputable': True},
    {'codigo': '4.2.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS DE MARKETING', 'es_imputable': False},
    {'codigo': '4.2.02.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SALARIOS PERSONAL MARKETING', 'es_imputable': True},
    {'codigo': '4.2.02.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'PRESTACIONES PERSONAL MARKETING', 'es_imputable': True},
    {'codigo': '4.2.02.03.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'PUBLICIDAD Y PROMOCIÓN', 'es_imputable': True},
    {'codigo': '4.2.03.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTO PERSONAL TÉCNICO (TIEMPO OCIOSO)', 'es_imputable': False},
    {'codigo': '4.2.03.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SALARIOS PERSONAL TÉCNICO OCIOSO', 'es_imputable': True},
    {'codigo': '4.2.03.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'PRESTACIONES PERSONAL TÉCNICO OCIOSO', 'es_imputable': True},
    {'codigo': '4.2.04.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS DE TECNOLOGÍA (NO ASIGNADOS)', 'es_imputable': False},
    {'codigo': '4.2.04.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'LICENCIAS Y SUSCRIPCIONES', 'es_imputable': True},
    {'codigo': '4.2.04.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'DEPRECIACIÓN EQUIPO INFORMÁTICO (USO GENERAL)', 'es_imputable': True},
    {'codigo': '4.2.04.03.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'MANTENIMIENTO EQUIPO INFORMÁTICO', 'es_imputable': True},

    # Ingresos
    {'codigo': '5.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'INGRESOS', 'es_imputable': False},
    {'codigo': '5.1.01.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'INGRESOS POR PROYECTO DE SOFTWARE', 'es_imputable': True},
    {'codigo': '5.1.02.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'OTROS INGRESOS', 'es_imputable': True},
    {'codigo': '5.1.03.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'GANANCIA EN VENTA DE ACTIVOS FIJOS', 'es_imputable': True},
    {'codigo': '5.1.04.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'PRODUCTOS FINANCIEROS', 'es_imputable': True},
]

def cargar_cuentas():
    """
    Itera sobre la lista de cuentas y las crea o actualiza en la BD.
    """
    print("Iniciando la carga del catálogo de cuentas...")
    creadas_count = 0
    actualizadas_count = 0

    for data in cuentas_data:
        codigo = data['codigo'].strip()
        tipo_fuente = data['tipoDeCuenta']
        nombre = data['nombreDeCuenta']
        # *** MODIFICADO: Capturar el nuevo valor ***
        es_imputable = data['es_imputable'] 

        # 4. Asignar el tipo de cuenta correcto desde el mapeo
        tipo_destino = TIPO_MAP.get(tipo_fuente)

        # Fallback por si falta un mapeo
        if not tipo_destino:
            print(f"ADVERTENCIA: No se encontró mapeo para '{tipo_fuente}' (Código: {codigo}). Omitiendo.")
            continue

        # 5. Usar update_or_create para crear o actualizar
        obj, created = Cuenta.objects.update_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'tipo_cuenta': tipo_destino,
                # *** MODIFICADO: Añadir el campo al crear/actualizar ***
                'es_imputable': es_imputable 
            }
        )

        if created:
            creadas_count += 1
        else:
            actualizadas_count += 1

    print("-" * 30)
    print("Carga completada con éxito. ✅")
    print(f"Cuentas nuevas creadas: {creadas_count}")
    print(f"Cuentas existentes actualizadas: {actualizadas_count}")
    print(f"Total de cuentas procesadas: {len(cuentas_data)}")

# --- Ejecutar el script ---
if __name__ == "__main__":
    cargar_cuentas()