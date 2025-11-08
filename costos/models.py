from django.db import models
from decimal import Decimal
from django.utils import timezone
# Importar la tabla de parámetros globales (ajusta la ruta si tu app se llama distinto)
from libromayor.models import ParametrosGlobales  


class Proyecto(models.Model):
    ESTADO_CHOICES = [
        ('PRE', 'Presupuesto'),
        ('ESP', 'Esperando Anticipo'),
        ('PRO', 'En Proceso'),
        ('FAC', 'Facturado'),
        ('COM', 'Completado'),
        ('CAN', 'Cancelado'),
    ]

    nombre = models.CharField(max_length=255)
    cliente = models.CharField(max_length=255)
    duracion_estimada = models.DurationField(null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True, editable=False)
    fecha_fin_estimada = models.DateField(null=True, blank=True, editable=False)

    anticipo = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Costo Estimado (Mano de Obra + Indirectos)
    costo_total_estimado = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Costo total ESTIMADO (Mano de Obra Estimada + Indirectos Asignados)",
        null=True, blank=True, editable=False
    )

    # IVA calculado automáticamente desde ParametrosGlobales
    iva = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        editable=False, null=True, blank=True,
        help_text="IVA calculado automáticamente según ParametrosGlobales"
    )

    estado = models.CharField(max_length=3, choices=ESTADO_CHOICES, default='PRE')
    anticipo_pagado = models.BooleanField(default=False, editable=False)

    # --- MÉTODOS DE NEGOCIO ---

    def __str__(self):
        return self.nombre

    @property
    def total_con_iva(self):
        """
        Retorna el total facturable (precio de venta + IVA).
        """
        return (self.precio_venta or Decimal('0.00')) + (self.iva or Decimal('0.00'))

    def marcar_anticipo_pagado(self):
        """
        Acción al presionar el botón 'Anticipo Pagado'.
        (La lógica de asientos contables puede implementarse en servicios o señales.)
        """
        pass  # Dejas esto para implementar en vistas o lógica de negocio posterior.

    def calcular_y_guardar_costo_estimado(self):
        """
        Calcula el costo total estimado sumando mano de obra directa
        y costos indirectos asignados según las horas estimadas.
        DEBE LLAMARSE DESPUÉS de haber creado los registros de HorasEstimadasEmpleado.
        """
        costo_mano_obra = Decimal('0.00')
        total_horas_estimadas = Decimal('0.00')

        # Sumar costo de mano de obra y horas totales
        for he in self.horas_estimadas.all():  # type: ignore
            if he.empleado.costo_real_hora_ajustado and he.horas_estimadas:
                costo_mano_obra += he.horas_estimadas * he.empleado.costo_real_hora_ajustado
                total_horas_estimadas += he.horas_estimadas

        # Obtener tasa de indirectos global
        try:
            params = ParametrosGlobales.objects.first()
            tasa_indirectos = params.tasa_gastos_indirectos_por_hora if params else Decimal('0.00')
        except Exception as e:
            print(f"ERROR: No se encontró ParametrosGlobales ({e})")
            tasa_indirectos = Decimal('0.00')

        # Calcular indirectos asignados
        costo_indirectos_asignados = total_horas_estimadas * tasa_indirectos

        # Guardar el costo total estimado
        self.costo_total_estimado = round(costo_mano_obra + costo_indirectos_asignados, 2)
        self.save(update_fields=['costo_total_estimado'])

    def calcular_y_guardar_iva(self):
        """
        Calcula y guarda el valor del IVA usando el porcentaje definido en ParametrosGlobales.
        Se aplica sobre el precio_venta.
        """
        try:
            params = ParametrosGlobales.objects.first()
            tasa_iva = params.porcentaje_iva if params else Decimal('0.00')
        except Exception as e:
            print(f"Error obteniendo ParametrosGlobales: {e}")
            tasa_iva = Decimal('0.00')

        self.iva = round(self.precio_venta * tasa_iva, 2)
        self.save(update_fields=['iva'])

    def save(self, *args, **kwargs):
        """
        Guarda el proyecto y calcula automáticamente el IVA según el precio de venta actual.
        """
        super().save(*args, **kwargs)
        if self.precio_venta > 0:
            try:
                params = ParametrosGlobales.objects.first()
                tasa_iva = params.porcentaje_iva if params else Decimal('0.00')
                nuevo_iva = round(self.precio_venta * tasa_iva, 2)
                if nuevo_iva != self.iva:
                    self.iva = nuevo_iva
                    super().save(update_fields=['iva'])
            except Exception as e:
                print(f"Error calculando IVA: {e}")


class HorasEstimadasEmpleado(models.Model):
    """
    Guarda las HORAS ESTIMADAS por empleado para un proyecto.
    """
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="horas_estimadas"
    )
    empleado = models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.PROTECT,
        related_name="proyectos_asignados"
    )
    horas_estimadas = models.DecimalField(
        max_digits=7, decimal_places=2,
        help_text="Total de horas estimadas para este empleado en el proyecto"
    )

    class Meta:
        verbose_name_plural = "Horas Estimadas por Empleado"
        unique_together = ('proyecto', 'empleado')

    def __str__(self):
        return f"{self.empleado.nombre} - {self.proyecto.nombre}: {self.horas_estimadas} hrs (Estimadas)"
