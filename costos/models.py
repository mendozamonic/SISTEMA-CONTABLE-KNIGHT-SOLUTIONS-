from django.db import models
from decimal import Decimal
from datetime import date, timedelta  # ✅ ← IMPORT NECESARIO
from django.utils import timezone
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

    # Fechas y duración
    fecha_inicio = models.DateField(null=True, blank=True, editable=False)
    fecha_fin_estimada = models.DateField(null=True, blank=True, editable=True)
    duracion_estimada = models.DurationField(null=True, blank=True, editable=False)

    # Costos y precios
    costo_total_estimado = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Costo total estimado (mano de obra + indirectos)",
        editable=True
    )
    ganancia_porcentaje = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.00'),
        help_text="Porcentaje de ganancia aplicado al costo total."
    )
    precio_venta = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Precio de venta sin IVA (calculado automáticamente)"
    )

    # IVA y total con IVA
    iva = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    precio_total_con_iva = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Precio final (precio de venta + IVA)"
    )

    # Anticipo
    anticipo_porcentaje = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.00'),
        help_text="Porcentaje del anticipo aplicado sobre el total con IVA"
    )
    anticipo = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Valor monetario del anticipo calculado automáticamente"
    )

    estado = models.CharField(max_length=3, choices=ESTADO_CHOICES, default='PRE')
    anticipo_pagado = models.BooleanField(default=False, editable=False)
    completo_pagado = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return self.nombre

    # ---------------- MÉTODOS ---------------- #

    def calcular_duracion(self):
        """Duración en días según las horas estimadas (8h = 1 día)."""
        total_horas = sum((he.horas_estimadas for he in self.horas_estimadas.all()), Decimal('0.00')) # type: ignore
        if total_horas > 0:
            dias = float(total_horas) / 8.0
            self.fecha_inicio = date.today()
            self.duracion_estimada = timedelta(days=dias)
            self.fecha_fin_estimada = self.fecha_inicio + self.duracion_estimada
            self.save(update_fields=['fecha_inicio', 'duracion_estimada', 'fecha_fin_estimada'])

    def calcular_costo_estimado(self):
        """Costo = Mano de obra + Indirectos."""
        from libromayor.models import ParametrosGlobales
        costo_mano_obra = Decimal('0.00')
        total_horas = Decimal('0.00')

        for he in self.horas_estimadas.all():  # type: ignore
            if he.empleado.costo_real_hora_ajustado and he.horas_estimadas:
                costo_mano_obra += he.horas_estimadas * he.empleado.costo_real_hora_ajustado
                total_horas += he.horas_estimadas

        try:
            params = ParametrosGlobales.objects.first()
            tasa_indirectos = params.tasa_gastos_indirectos_por_hora if params else Decimal('0.00')
        except Exception:
            tasa_indirectos = Decimal('0.00')

        costo_indirectos = total_horas * tasa_indirectos
        self.costo_total_estimado = round(costo_mano_obra + costo_indirectos, 2)
        self.save(update_fields=['costo_total_estimado'])

    def calcular_precio(self):
        """Precio = costo + ganancia%"""
        if self.costo_total_estimado > 0:
            self.precio_venta = round(self.costo_total_estimado * (1 + self.ganancia_porcentaje / 100), 2)
            self.save(update_fields=['precio_venta'])

    def calcular_iva(self):
        """IVA = precio * porcentaje global"""
        try:
            params = ParametrosGlobales.objects.first()
            tasa_iva = params.porcentaje_iva if params else Decimal('0.00')
        except Exception:
            tasa_iva = Decimal('0.00')

        self.iva = round(self.precio_venta * tasa_iva, 2)
        self.precio_total_con_iva = round(self.precio_venta + self.iva, 2)
        self.save(update_fields=['iva', 'precio_total_con_iva'])

    def calcular_anticipo(self):
        """Anticipo = total con IVA * porcentaje anticipo"""
        if self.precio_total_con_iva > 0:
            self.anticipo = round(self.precio_total_con_iva * (self.anticipo_porcentaje / 100), 2)
            self.save(update_fields=['anticipo'])

    def calcular_todo(self):
        """
        Realiza el flujo completo:
        Duración → Costo → Precio → IVA → Total con IVA → Anticipo
        """
        self.calcular_duracion()
        self.calcular_costo_estimado()
        self.calcular_precio()
        self.calcular_iva()
        self.calcular_anticipo()

    def save(self, *args, **kwargs):
        """Guarda y asegura coherencia."""
        super().save(*args, **kwargs)
        # Cada vez que se guarda, recalcula IVA y total con IVA.



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
