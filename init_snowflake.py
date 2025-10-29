from app.db.snowflake_db import init_snowflake, migrate_from_sqlite

if __name__ == "__main__":
    print("Inicializando base de datos en Snowflake...")
    if init_snowflake():
        print("Migrando datos desde SQLite...")
        migrate_from_sqlite()
        print("¡Migración completada!")
    else:
        print("Error inicializando Snowflake")