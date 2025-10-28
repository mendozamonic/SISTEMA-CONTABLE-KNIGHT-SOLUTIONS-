import os
import django
import sys
from decimal import Decimal

# --- Configuración de Django ---
# Asegúrate de que 'sistemacontable.settings' sea el nombre correcto
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
#    Usamos los valores del modelo para que sea más robusto
TIPO_MAP = {
    'Activo': Cuenta.TipoCuenta.ACTIVO,
    'Pasivo': Cuenta.TipoCuenta.PASIVO,
    'Patrimonio': Cuenta.TipoCuenta.PATRIMONIO,
    'Ingreso': Cuenta.TipoCuenta.INGRESO,
    'Gasto': Cuenta.TipoCuenta.GASTO,
    'Costo': Cuenta.TipoCuenta.COSTO,
}

# 3. Catálogo de cuentas adaptado a tu lista
#    El 'tipoDeCuenta' se infiere del código (1=Activo, 2=Pasivo, 3=Patrimonio, 4.1=Costo, 4.2=Gasto, 5=Ingreso)
cuentas_data = [
    # Activos
    {'codigo': '1.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'ACTIVO'},
    {'codigo': '1.1.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'ACTIVO CORRIENTE'},
    {'codigo': '1.1.01.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'CAJA Y BANCOS'},
    {'codigo': '1.1.01.01.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'CAJA GENERAL'},
    {'codigo': '1.1.01.02.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'BANCOS'},
    {'codigo': '1.1.02.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'CUENTAS POR COBRAR'},
    {'codigo': '1.1.02.01.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'CLIENTES'},
    {'codigo': '1.1.02.02.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'ESTIMACIÓN CUENTAS INCOBRABLES (-)'},
    {'codigo': '1.1.03.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'IVA CRÉDITO FISCAL'},
    {'codigo': '1.1.04.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'INVENTARIO DE PROYECTOS EN PROCESO'},
    {'codigo': '1.2.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'ACTIVO NO CORRIENTE'},
    {'codigo': '1.2.01.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'MOBILIARIO Y EQUIPO'},
    {'codigo': '1.2.02.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'EQUIPO INFORMÁTICO'},
    {'codigo': '1.2.03.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'DEPRECIACIÓN ACUMULADA'},
    {'codigo': '1.2.03.01.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'DEPR. ACUM. MOBILIARIO Y EQUIPO (-)'},
    {'codigo': '1.2.03.02.', 'tipoDeCuenta': 'Activo', 'nombreDeCuenta': 'DEPR. ACUM. EQUIPO INFORMÁTICO (-)'},
    
    # Pasivos
    {'codigo': '2.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'PASIVO'},
    {'codigo': '2.1.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'PASIVO CORRIENTE'},
    {'codigo': '2.1.01.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'CUENTAS POR PAGAR'},
    {'codigo': '2.1.01.01.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'PROVEEDORES LOCALES'},
    {'codigo': '2.1.01.02.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'SERVICIOS DE TERCEROS'},
    {'codigo': '2.1.02.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'IVA DÉBITO FISCAL'},
    {'codigo': '2.1.03.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'IMPUESTO SOBRE LA RENTA POR PAGAR'},
    {'codigo': '2.1.04.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'ANTICIPOS DE CLIENTES'},
    {'codigo': '2.1.05.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'NÓMINA POR PAGAR'},
    {'codigo': '2.1.05.01.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'SUELDOS POR PAGAR'},
    {'codigo': '2.1.05.02.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'COTIZACIONES AFP POR PAGAR'},
    {'codigo': '2.1.05.03.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'COTIZACIONES ISSS POR PAGAR'},
    {'codigo': '2.1.05.04.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'PROVISIÓN AGUINALDO'},
    {'codigo': '2.1.05.05.', 'tipoDeCuenta': 'Pasivo', 'nombreDeCuenta': 'PROVISIÓN VACACIONES'},

    # Patrimonio
    {'codigo': '3.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'PATRIMONIO'},
    {'codigo': '3.1.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'CAPITAL'},
    {'codigo': '3.1.01.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'CAPITAL SOCIAL'},
    {'codigo': '3.2.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'UTILIDADES'},
    {'codigo': '3.2.01.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'UTILIDAD DEL EJERCICIO'},
    {'codigo': '3.2.02.', 'tipoDeCuenta': 'Patrimonio', 'nombreDeCuenta': 'UTILIDADES ACUMULADAS'},

    # Costos y Gastos
    {'codigo': '4.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'COSTOS Y GASTOS DE OPERACIÓN'}, # Padre general de gastos
    {'codigo': '4.1.', 'tipoDeCuenta': 'Costo', 'nombreDeCuenta': 'COSTO DE VENTA'},
    {'codigo': '4.1.01.', 'tipoDeCuenta': 'Costo', 'nombreDeCuenta': 'COSTO DE VENTA'}, # Nombre limpiado
    {'codigo': '4.2.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS DE OPERACIÓN'},
    {'codigo': '4.2.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS DE ADMINISTRACIÓN'},
    {'codigo': '4.2.01.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SALARIOS PERSONAL ADMIN.'},
    {'codigo': '4.2.01.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'PRESTACIONES PERSONAL ADMIN.'},
    {'codigo': '4.2.01.03.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'ALQUILER LOCAL'},
    {'codigo': '4.2.01.04.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SERVICIOS BÁSICOS'},
    {'codigo': '4.2.01.05.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SERVICIOS DE TERCEROS'},
    {'codigo': '4.2.01.06.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'DEPRECIACIÓN MOBILIARIO Y EQUIPO'},
    {'codigo': '4.2.01.07.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SUMINISTROS DE OFICINA'},
    {'codigo': '4.2.01.08.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'MANTENIMIENTO Y REPARACIONES'},
    {'codigo': '4.2.01.09.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS VARIOS'},
    {'codigo': '4.2.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS DE MARKETING'},
    {'codigo': '4.2.02.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SALARIOS PERSONAL MARKETING'},
    {'codigo': '4.2.02.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'PRESTACIONES PERSONAL MARKETING'},
    {'codigo': '4.2.02.03.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'PUBLICIDAD Y PROMOCIÓN'},
    {'codigo': '4.2.03.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTO PERSONAL TÉCNICO (TIEMPO OCIOSO)'},
    {'codigo': '4.2.03.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'SALARIOS PERSONAL TÉCNICO OCIOSO'},
    {'codigo': '4.2.03.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'PRESTACIONES PERSONAL TÉCNICO OCIOSO'},
    {'codigo': '4.2.04.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'GASTOS DE TECNOLOGÍA (NO ASIGNADOS)'},
    {'codigo': '4.2.04.01.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'LICENCIAS Y SUSCRIPCIONES'},
    {'codigo': '4.2.04.02.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'DEPRECIACIÓN EQUIPO INFORMÁTICO (USO GENERAL)'},
    {'codigo': '4.2.04.03.', 'tipoDeCuenta': 'Gasto', 'nombreDeCuenta': 'MANTENIMIENTO EQUIPO INFORMÁTICO'},

    # Ingresos
    {'codigo': '5.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'INGRESOS'}, # Cuenta padre agregada
    {'codigo': '5.1.01.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'INGRESOS POR PROYECTO DE SOFTWARE'},
    {'codigo': '5.1.02.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'OTROS INGRESOS'},
    {'codigo': '5.1.03.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'GANANCIA EN VENTA DE ACTIVOS FIJOS'},
    {'codigo': '5.1.04.', 'tipoDeCuenta': 'Ingreso', 'nombreDeCuenta': 'PRODUCTOS FINANCIEROS'},
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

        # 4. Asignar el tipo de cuenta correcto desde el mapeo
        tipo_destino = TIPO_MAP.get(tipo_fuente)

        # Fallback por si falta un mapeo
        if not tipo_destino:
            print(f"ADVERTENCIA: No se encontró mapeo para '{tipo_fuente}' (Código: {codigo}). Omitiendo.")
            continue

        # 5. Usar update_or_create para crear o actualizar
        # Busca por 'codigo', y si existe, actualiza los 'defaults'.
        # Si no existe, crea uno nuevo con 'codigo' y los 'defaults'.
        obj, created = Cuenta.objects.update_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'tipo_cuenta': tipo_destino
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