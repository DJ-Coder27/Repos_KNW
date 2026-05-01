import os
import pymssql


def get_db_connection():
    server = os.getenv("AZURE_SQL_SERVER")
    database = os.getenv("AZURE_SQL_DATABASE")
    username = os.getenv("AZURE_SQL_USERNAME")
    password = os.getenv("AZURE_SQL_PASSWORD")

    if not all([server, database, username, password]):
        raise RuntimeError("Azure SQL environment variables are not fully configured.")

    return pymssql.connect(
        server=server,
        user=username,
        password=password,
        database=database,
        port=1433,
        tds_version="7.4",
        login_timeout=30,
        timeout=30
    )


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        IF OBJECT_ID('dbo.metrics', 'U') IS NULL
        BEGIN
            CREATE TABLE dbo.metrics (
                id INT IDENTITY(1,1) PRIMARY KEY,
                device_name NVARCHAR(100) NOT NULL,
                cpu_usage FLOAT NOT NULL,
                memory_usage FLOAT NOT NULL,
                disk_usage FLOAT NOT NULL,
                status NVARCHAR(50) NOT NULL,
                timestamp DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
            );
        END
    """)

    conn.commit()
    conn.close()