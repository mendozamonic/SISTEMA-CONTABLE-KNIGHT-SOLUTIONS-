from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP, getcontext
from libromayor.models import ParametrosGlobales 

# Set precision for Decimal operations
getcontext().prec = 28

# --- CONSTANTES DE CÁLCULO (El Salvador) ---
DIAS_MES = Decimal('30')
LIMITE_ISSS_COTIZABLE = Decimal('1000.00') # Límite Máximo Cotizable ISSS

# TABLA DE RETENCIÓN DE RENTA MENSUAL (ISR - El Salvador)
# [Límite Inferior, Límite Superior, Porcentaje, Cuota Fija, Sobre el Exceso de]
TABLA_ISR_MENSUAL = [
    (Decimal('0.01'), Decimal('472.00'), Decimal('0.00'), Decimal('0.00'), Decimal('0.00')), 
    (Decimal('472.01'), Decimal('895.24'), Decimal('0.10'), Decimal('17.67'), Decimal('472.00')), 
    (Decimal('895.25'), Decimal('2038.10'), Decimal('0.20'), Decimal('60.00'), Decimal('895.24')), 
    (Decimal('2038.11'), Decimal('999999.00'), Decimal('0.30'), Decimal('288.57'), Decimal('2038.10')), 
]


class Empleado(models.Model):
    """
    Información del empleado. Calcula y guarda automáticamente 
    costo por hora y datos de planilla mensual al guardar.
    """
    # --- DATOS BÁSICOS ---
    nombre = models.CharField(max_length=255)
    cargo = models.CharField(max_length=150)
    salario_diario = models.DecimalField(max_digits=10, decimal_places=2, help_text="Salario base por día trabajado")
    
    # --- PARÁMETROS ESPECÍFICOS DEL EMPLEADO (Input) ---
    dias_laborados_semana = models.IntegerField(null=True, blank=True)
    horas_laboradas_diarias = models.IntegerField(null=True, blank=True)
    dias_vacaciones_anual = models.IntegerField(null=True, blank=True)
    recargo_vacaciones = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dias_aguinaldo_anual = models.IntegerField(null=True, blank=True)
    eficiencia = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # --- RESULTADOS CALCULADOS (Output - editable=False) ---
    costo_real_hora_ajustado = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True, editable=False)
    salario_bruto_mensual_calculado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)
    aporte_patronal_isss_mensual = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)
    aporte_patronal_afp_mensual = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)
    deduccion_isss_mensual = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)
    deduccion_afp_mensual = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)
    deduccion_renta_mensual = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)
    total_deducciones_mensual = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)
    pago_liquido_mensual = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)

    def __str__(self):
        return self.nombre

    # ----------------------------------------
    # I. Lógica de Parámetros y Defaults
    # ----------------------------------------

    def get_parametros_globales(self):
        """Asume que la instancia existe."""
        return ParametrosGlobales.objects.get()
            
    def set_defaults_from_globales(self):
        """Establece valores por defecto si los campos están vacíos."""
        params = self.get_parametros_globales()

        if self.dias_laborados_semana is None: self.dias_laborados_semana = params.dias_laborados_semana
        if self.horas_laboradas_diarias is None: self.horas_laboradas_diarias = params.horas_laboradas_diarias
        if self.recargo_vacaciones is None: self.recargo_vacaciones = params.recargo_vacaciones
        # Usamos defaults del sistema si no están en PG (asumiendo 15 días estándar)
        if self.dias_aguinaldo_anual is None: self.dias_aguinaldo_anual = 15 
        if self.dias_vacaciones_anual is None: self.dias_vacaciones_anual = 15 
        if self.eficiencia is None: self.eficiencia = params.eficiencia_base

    def _set_calculated_fields_to_none(self):
        """Limpia campos calculados en caso de error de cálculo."""
        self.costo_real_hora_ajustado = None
        self.salario_bruto_mensual_calculado = None
        self.aporte_patronal_isss_mensual = None
        self.aporte_patronal_afp_mensual = None
        self.deduccion_isss_mensual = None
        self.deduccion_afp_mensual = None
        self.deduccion_renta_mensual = None
        self.total_deducciones_mensual = None
        self.pago_liquido_mensual = None

    # ----------------------------------------
    # II. Lógica de Cálculo de Planilla (Payroll Calculation Logic)
    # ----------------------------------------

    def _calcular_deduccion_renta(self, salario_base, deduccion_isss, deduccion_afp):
        """Calcula la retención de Impuesto Sobre la Renta (ISR) mensual."""
        
        renta_gravable = salario_base - deduccion_isss - deduccion_afp
        
        for _, limite_superior, porcentaje, cuota_fija, sobre_exceso in TABLA_ISR_MENSUAL:
            
            if renta_gravable <= limite_superior:
                if porcentaje == Decimal('0.00'):
                    return Decimal('0.00') 
                
                exceso = renta_gravable - sobre_exceso
                impuesto_a_retener = cuota_fija + (exceso * porcentaje)
                
                return impuesto_a_retener.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                
        return Decimal('0.00')

    def _calcular_datos_planilla_mensual(self, params):
        """Calcula todos los datos de planilla mensual: Bruto, Aportes, Deducciones, Líquido."""
        if self.salario_diario is None: return None
        
        # Conversión a Decimal y manejo de None
        try:
            salario_diario = Decimal(self.salario_diario)
            dias_vacaciones_anual = Decimal(self.dias_vacaciones_anual or 0)
            recargo_vacaciones = Decimal(self.recargo_vacaciones or 0)
            dias_aguinaldo_anual = Decimal(self.dias_aguinaldo_anual or 0)
        except:
             return None 

        # 1. SALARIO BRUTO (Base + Acumulados)
        salario_base_30_dias = salario_diario * DIAS_MES
        dias_vacacion_pagados = dias_vacaciones_anual * (Decimal('1') + recargo_vacaciones)
        acumulado_vacaciones = (salario_diario * dias_vacacion_pagados) / Decimal('12')
        acumulado_aguinaldo = (salario_diario * dias_aguinaldo_anual) / Decimal('12')
        salario_bruto_mensual = salario_base_30_dias + acumulado_vacaciones + acumulado_aguinaldo
        
        # 2. BASES Y APORTES
        base_cotizacion = salario_base_30_dias
        base_isss = min(base_cotizacion, LIMITE_ISSS_COTIZABLE)
        limite_afp = getattr(params, 'limite_afp', Decimal('999999.00')) 
        base_afp = min(base_cotizacion, limite_afp) 
        
        aporte_patronal_isss = base_isss * params.patronal_seguro_social
        aporte_patronal_afp = base_afp * params.patronal_afp
        
        deduccion_isss = base_isss * params.empleado_seguro_social
        deduccion_afp = base_afp * params.empleado_afp
        
        # 3. DEDUCCIÓN DE RENTA
        deduccion_renta = self._calcular_deduccion_renta(
            salario_base=salario_base_30_dias, 
            deduccion_isss=deduccion_isss, 
            deduccion_afp=deduccion_afp
        )
        
        # 4. TOTALES Y LÍQUIDO
        total_deducciones = deduccion_isss + deduccion_afp + deduccion_renta
        pago_liquido = salario_bruto_mensual - total_deducciones
        
        # Retornar los valores redondeados
        data = {
            'bruto': salario_bruto_mensual,
            'aporte_patronal_isss': aporte_patronal_isss,
            'aporte_patronal_afp': aporte_patronal_afp,
            'deduccion_isss': deduccion_isss,
            'deduccion_afp': deduccion_afp,
            'deduccion_renta': deduccion_renta,
            'total_deducciones': total_deducciones,
            'pago_liquido': pago_liquido
        }
        return {k: v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) for k, v in data.items()}

    def _calcular_costo_real(self, params):
        """Calcula el costo real por hora, incluyendo gastos indirectos."""
        
        try:
            salario_diario = Decimal(self.salario_diario)
            # ... (Conversión de todos los campos necesarios)
            dias_vacaciones_anual = Decimal(self.dias_vacaciones_anual or 0)
            recargo_vacaciones = Decimal(self.recargo_vacaciones or 0)
            dias_aguinaldo_anual = Decimal(self.dias_aguinaldo_anual or 0)
            dias_laborados_semana = Decimal(self.dias_laborados_semana or 0)
            horas_laboradas_diarias = Decimal(self.horas_laboradas_diarias or 0)
            eficiencia = Decimal(self.eficiencia or 1.0) 
            tasa_gi = Decimal(params.tasa_gastos_indirectos_por_hora or 0)
        except:
             return None

        # Cálculos de provisión semanal (Base para Costo por Hora)
        salario_septimo = salario_diario * 7
        costo_anual_vac = salario_diario * dias_vacaciones_anual * (Decimal('1') + recargo_vacaciones)
        prov_sem_vac = (costo_anual_vac / Decimal('365')) * 7
        costo_anual_agui = salario_diario * dias_aguinaldo_anual
        prov_sem_agui = (costo_anual_agui / Decimal('365')) * 7
        
        base_cotizacion_semanal = salario_septimo + prov_sem_vac
        costo_sem_isss = base_cotizacion_semanal * params.patronal_seguro_social 
        costo_sem_afp = base_cotizacion_semanal * params.patronal_afp
        
        costo_real_semanal = (salario_septimo + prov_sem_vac + prov_sem_agui + costo_sem_isss + costo_sem_afp)
        
        # Costo por Hora
        horas_semanales_laboradas = dias_laborados_semana * horas_laboradas_diarias
        if horas_semanales_laboradas == 0: return Decimal('0.0000')
        
        costo_real_hora_sin_indirectos = costo_real_semanal / horas_semanales_laboradas
        
        # Aplicar Gastos Indirectos y Eficiencia
        costo_hora_con_indirectos = costo_real_hora_sin_indirectos + tasa_gi
        if eficiencia <= 0: return None 
        costo_real_final = costo_hora_con_indirectos / eficiencia
        
        return costo_real_final.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)

    # ----------------------------------------
    # III. Método SAVE Principal
    # ----------------------------------------

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        params = self.get_parametros_globales()

        # 1. Establecer Defaults si el empleado es nuevo
        if is_new:
            self.set_defaults_from_globales()
        
        # 2. Realizar Cálculos
        try:
            self.costo_real_hora_ajustado = self._calcular_costo_real(params) 
            planilla_data = self._calcular_datos_planilla_mensual(params)
            
            if planilla_data:
                # Asignación de todos los campos calculados
                self.salario_bruto_mensual_calculado = planilla_data['bruto']
                self.aporte_patronal_isss_mensual = planilla_data['aporte_patronal_isss']
                self.aporte_patronal_afp_mensual = planilla_data['aporte_patronal_afp']
                self.deduccion_isss_mensual = planilla_data['deduccion_isss']
                self.deduccion_afp_mensual = planilla_data['deduccion_afp']
                self.deduccion_renta_mensual = planilla_data['deduccion_renta']
                self.total_deducciones_mensual = planilla_data['total_deducciones']
                self.pago_liquido_mensual = planilla_data['pago_liquido']
            else: 
                self._set_calculated_fields_to_none()

        except Exception as e: 
             print(f"Error inesperado al calcular datos para empleado {self.nombre}: {e}")
             self._set_calculated_fields_to_none()

        super().save(*args, **kwargs)