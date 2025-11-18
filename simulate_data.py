"""
Script para generar datos simulados de checklists con diferentes niveles de cumplimiento.
Esto permite visualizar cómo el aumento del cumplimiento afecta los indicadores CLMC y TEAEM.
"""
import sqlite3
from datetime import datetime, timedelta
import random

def generate_simulated_data():
    """
    Genera datos simulados con diferentes escenarios:
    - Escenario 1: Cumplimiento bajo (40-60%) - Semana -4
    - Escenario 2: Cumplimiento medio (60-80%) - Semana -3
    - Escenario 3: Cumplimiento bueno (80-90%) - Semana -2
    - Escenario 4: Cumplimiento excelente (90-100%) - Semana -1 (actual)
    """
    
    conn = sqlite3.connect('medcheck.db')
    cursor = conn.cursor()
    
    # Limpiar datos anteriores (opcional - comentar si quieres mantener datos reales)
    print("⚠️  Limpiando datos antiguos de administración...")
    cursor.execute("DELETE FROM checklist_entries WHERE protocolo_etapa = 'administracion'")
    conn.commit()
    
    now = datetime.now()
    total_entries = 0
    
    # Definir escenarios por semana
    scenarios = [
        {
            'name': 'Cumplimiento Bajo (Semana -4)',
            'weeks_ago': 4,
            'entries_per_day': 3,
            'compliance_rate': 0.40,  # 40% de cumplimiento
            'days': 7
        },
        {
            'name': 'Cumplimiento Medio-Bajo (Semana -3)',
            'weeks_ago': 3,
            'entries_per_day': 4,
            'compliance_rate': 0.60,  # 60% de cumplimiento
            'days': 7
        },
        {
            'name': 'Cumplimiento Bueno (Semana -2)',
            'weeks_ago': 2,
            'entries_per_day': 5,
            'compliance_rate': 0.85,  # 85% de cumplimiento
            'days': 7
        },
        {
            'name': 'Cumplimiento Excelente (Semana -1 y actual)',
            'weeks_ago': 1,
            'entries_per_day': 6,
            'compliance_rate': 0.95,  # 95% de cumplimiento
            'days': 10  # Más días para simular semana actual
        }
    ]
    
    areas = ['Urgencias', 'Hospitalización', 'UCI', 'Pediatría']
    turnos = ['Matutino', 'Vespertino', 'Nocturno']
    usuarios = ['Enf. María González', 'Enf. Juan Pérez', 'Enf. Ana Martínez', 'Enf. Carlos López']
    
    print("\n" + "="*70)
    print("🎯 GENERANDO DATOS SIMULADOS PARA ANÁLISIS DE TENDENCIAS")
    print("="*70 + "\n")
    
    for scenario in scenarios:
        print(f"\n📊 {scenario['name']}")
        print(f"   Tasa de cumplimiento esperada: {scenario['compliance_rate']*100:.0f}%")
        print(f"   Generando {scenario['entries_per_day']} administraciones por día durante {scenario['days']} días...")
        
        scenario_entries = 0
        scenario_compliant = 0
        
        for day in range(scenario['days']):
            date_offset = timedelta(weeks=scenario['weeks_ago'], days=day)
            entry_date = now - date_offset
            
            for entry_num in range(scenario['entries_per_day']):
                # Determinar si esta entrada será completa o tendrá errores
                is_compliant = random.random() < scenario['compliance_rate']
                
                # Generar valores para los 10 correctos
                if is_compliant:
                    # Todos los correctos marcados (100% cumplimiento)
                    correctos = {
                        'paciente_correcto': 1,
                        'medicamento_correcto': 1,
                        'dosis_correcta': 1,
                        'via_correcta': 1,
                        'hora_correcta': 1,
                        'fecha_vencimiento_verificada': 1,
                        'educacion_paciente': 1,
                        'registro_correcto': 1,
                        'alergias_verificadas': 1,
                        'responsabilidad_personal': 1
                    }
                    scenario_compliant += 1
                else:
                    # Generar errores aleatorios (1-3 correctos fallados)
                    num_errores = random.randint(1, 3)
                    correctos_keys = [
                        'paciente_correcto', 'medicamento_correcto', 'dosis_correcta', 
                        'via_correcta', 'hora_correcta', 'fecha_vencimiento_verificada',
                        'educacion_paciente', 'registro_correcto', 'alergias_verificadas',
                        'responsabilidad_personal'
                    ]
                    
                    # Todos en 1 inicialmente
                    correctos = {key: 1 for key in correctos_keys}
                    
                    # Marcar algunos como 0 (errores)
                    errores_keys = random.sample(correctos_keys, num_errores)
                    for key in errores_keys:
                        correctos[key] = 0
                
                # Insertar entrada en la base de datos
                cursor.execute("""
                    INSERT INTO checklist_entries (
                        fecha_hora, area, turno, protocolo_etapa, item, cumple, 
                        observaciones, usuario, metadatos,
                        paciente_correcto, medicamento_correcto, dosis_correcta,
                        via_correcta, hora_correcta, fecha_vencimiento_verificada,
                        educacion_paciente, registro_correcto, alergias_verificadas,
                        responsabilidad_personal
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry_date.isoformat(),
                    random.choice(areas),
                    random.choice(turnos),
                    'administracion',
                    'Administración de Medicamento',
                    1,
                    'Datos simulados para análisis de tendencias' if is_compliant else f'Simulación con {num_errores} error(es)',
                    random.choice(usuarios),
                    '{"simulado": true}',
                    correctos['paciente_correcto'],
                    correctos['medicamento_correcto'],
                    correctos['dosis_correcta'],
                    correctos['via_correcta'],
                    correctos['hora_correcta'],
                    correctos['fecha_vencimiento_verificada'],
                    correctos['educacion_paciente'],
                    correctos['registro_correcto'],
                    correctos['alergias_verificadas'],
                    correctos['responsabilidad_personal']
                ))
                
                scenario_entries += 1
                total_entries += 1
        
        conn.commit()
        
        # Calcular estadísticas reales del escenario
        actual_compliance = (scenario_compliant / scenario_entries) * 100
        actual_adverse = ((scenario_entries - scenario_compliant) / scenario_entries) * 100
        
        print(f"   ✅ Generadas {scenario_entries} administraciones")
        print(f"   📈 CLMC real: {actual_compliance:.1f}% ({scenario_compliant}/{scenario_entries} completas)")
        print(f"   ⚠️  TEAEM real: {actual_adverse:.1f}% ({scenario_entries - scenario_compliant}/{scenario_entries} con errores)")
    
    conn.close()
    
    print("\n" + "="*70)
    print(f"✨ COMPLETADO: {total_entries} administraciones simuladas generadas")
    print("="*70)
    print("\n💡 ANÁLISIS ESPERADO:")
    print("   • Semana -4: CLMC ~40%, TEAEM ~60% (Crítico)")
    print("   • Semana -3: CLMC ~60%, TEAEM ~40% (Alerta)")
    print("   • Semana -2: CLMC ~85%, TEAEM ~15% (Bueno)")
    print("   • Semana -1: CLMC ~95%, TEAEM ~5% (Excelente)")
    print("\n🔄 Recarga la página de Indicadores para ver los resultados!")
    print("   http://127.0.0.1:8002/indicadores-calidad\n")

if __name__ == "__main__":
    try:
        generate_simulated_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
