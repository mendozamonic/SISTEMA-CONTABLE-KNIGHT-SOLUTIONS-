"""
Management command to fix employees by ensuring ParametrosGlobales exists
and recalculating all employees.
Run with: python manage.py fix_empleados
"""
from django.core.management.base import BaseCommand
from empleados.models import Empleado
from libromayor.models import ParametrosGlobales


class Command(BaseCommand):
    help = 'Fix employees by ensuring ParametrosGlobales exists and recalculating all employees'

    def handle(self, *args, **options):
        # Step 1: Ensure ParametrosGlobales exists
        self.stdout.write(self.style.SUCCESS('\n=== Step 1: Checking ParametrosGlobales ==='))
        pg = ParametrosGlobales.objects.first()
        
        if not pg:
            self.stdout.write(self.style.WARNING('  ParametrosGlobales does not exist. Creating it...'))
            try:
                pg = ParametrosGlobales.objects.create()
                self.stdout.write(self.style.SUCCESS('  ✓ ParametrosGlobales created successfully!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error creating ParametrosGlobales: {e}'))
                return
        else:
            self.stdout.write(self.style.SUCCESS(f'  ✓ ParametrosGlobales already exists (ID: {pg.id})'))
            self.stdout.write(f'    - patronal_seguro_social: {pg.patronal_seguro_social}')
            self.stdout.write(f'    - patronal_afp: {pg.patronal_afp}')
            self.stdout.write(f'    - empleado_seguro_social: {pg.empleado_seguro_social}')
            self.stdout.write(f'    - empleado_afp: {pg.empleado_afp}')
        
        # Step 2: Recalculate all employees
        self.stdout.write(self.style.SUCCESS('\n=== Step 2: Recalculating Employees ==='))
        empleados = Empleado.objects.all()
        total = empleados.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING('  No employees found in database.'))
            return
        
        self.stdout.write(f'  Found {total} employee(s) to process...\n')
        
        success_count = 0
        error_count = 0
        
        for e in empleados:
            self.stdout.write(f'  Processing: {e.nombre} (ID: {e.id})...', ending=' ')
            try:
                # Re-save to trigger calculations
                e.save()
                self.stdout.write(self.style.SUCCESS('✓'))
                success_count += 1
            except Exception as ex:
                self.stdout.write(self.style.ERROR(f'✗ Error: {ex}'))
                error_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n=== Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Successfully recalculated: {success_count}/{total}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'  ✗ Errors: {error_count}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Done! Check the empleados table now.\n'))

