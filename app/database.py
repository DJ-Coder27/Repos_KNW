import os
import pyodbc

def get_db_connection():
    connection_string = os.getenv("AZURE_SQL_CONNECTION_STRING")

    if not connection_string:
        raise RuntimeError("AZURE_SQL_CONNECTION_STRING is not configured.")

    return pyodbc.connect(connection_string)


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sysobjects
            WHERE name = 'metrics' AND xtype = 'U'
        )
        CREATE TABLE metrics (
            id INT IDENTITY(1,1) PRIMARY KEY,
            device_name NVARCHAR(100) NOT NULL,
            cpu_usage FLOAT NOT NULL,
            memory_usage FLOAT NOT NULL,
            disk_usage FLOAT NOT NULL,
            status NVARCHAR(50) NOT NULL,
            timestamp DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
        );
    """)

    conn.commit()
    conn.close()