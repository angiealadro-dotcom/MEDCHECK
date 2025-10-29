from app.db.database import create_tables

if __name__ == "__main__":
    print("Creando tablas en la base de datos...")
    create_tables()
    print("¡Tablas creadas exitosamente!")