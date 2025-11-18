"""
Script de migración para agregar las columnas de los 10 correctos
a la tabla checklist_entries existente
"""
import sqlite3

def migrar_bd():
    conn = sqlite3.connect('medcheck.db')
    cursor = conn.cursor()
    
    # Lista de nuevas columnas a agregar
    columnas_nuevas = [
        'paciente_correcto',
        'medicamento_correcto',
        'dosis_correcta',
        'via_correcta',
        'hora_correcta',
        'fecha_vencimiento_verificada',
        'educacion_paciente',
        'registro_correcto',
        'alergias_verificadas',
        'responsabilidad_personal'
    ]
    
    # Verificar qué columnas ya existen
    cursor.execute("PRAGMA table_info(checklist_entries)")
    columnas_existentes = [col[1] for col in cursor.fetchall()]
    
    # Agregar solo las columnas que no existan
    for columna in columnas_nuevas:
        if columna not in columnas_existentes:
            try:
                sql = f"ALTER TABLE checklist_entries ADD COLUMN {columna} BOOLEAN DEFAULT 0"
                cursor.execute(sql)
                print(f"✅ Columna '{columna}' agregada exitosamente")
            except sqlite3.OperationalError as e:
                print(f"⚠️  Error agregando columna '{columna}': {e}")
        else:
            print(f"ℹ️  Columna '{columna}' ya existe")
    
    conn.commit()
    conn.close()
    print("\n✅ Migración completada")

if __name__ == "__main__":
    migrar_bd()
