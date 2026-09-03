"""
Stage 1: Migrate order_events data from local SQLite (orders.db) to Azure SQL.
Run this AFTER you've created the Azure SQL server + database (step-by-step below).

Requires: pip install pyodbc python-dotenv
Also requires the "ODBC Driver 18 for SQL Server" installed on Windows
(download: https://go.microsoft.com/fwlink/?linkid=2249006 if pyodbc can't find a driver)
"""
import sqlite3
import os
import pyodbc

# ---- Fill these in from your Azure SQL setup (Stage 1, step 3) ----
SERVER = os.environ.get("AZURE_SQL_SERVER", "your-server-name.database.windows.net")
DATABASE = os.environ.get("AZURE_SQL_DATABASE", "orderbridge-db")
USERNAME = os.environ.get("AZURE_SQL_USER", "your-admin-username")
PASSWORD = os.environ.get("AZURE_SQL_PASSWORD", "your-admin-password")
# ---------------------------------------------------------------------

CONN_STR = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER=tcp:{SERVER},1433;"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)


def main():
    print("Connecting to Azure SQL...")
    azure_conn = pyodbc.connect(CONN_STR)
    azure_cursor = azure_conn.cursor()

    print("Creating order_events table (if not exists)...")
    azure_cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='order_events' AND xtype='U')
        CREATE TABLE order_events (
            order_id INT,
            domain NVARCHAR(50),
            event_type NVARCHAR(50),
            timestamp NVARCHAR(50)
        )
    """)
    azure_conn.commit()

    print("Reading local SQLite data...")
    sqlite_conn = sqlite3.connect("orders.db")
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT order_id, domain, event_type, timestamp FROM order_events")
    rows = sqlite_cursor.fetchall()
    sqlite_conn.close()
    print(f"Found {len(rows)} rows to migrate.")

    print("Clearing existing Azure SQL data (idempotent re-run)...")
    azure_cursor.execute("DELETE FROM order_events")
    azure_conn.commit()

    print("Inserting rows into Azure SQL...")
    azure_cursor.executemany(
        "INSERT INTO order_events (order_id, domain, event_type, timestamp) VALUES (?, ?, ?, ?)",
        rows
    )
    azure_conn.commit()

    azure_cursor.execute("SELECT COUNT(*) FROM order_events")
    count = azure_cursor.fetchone()[0]
    print(f"Migration complete. Azure SQL now has {count} rows in order_events.")

    azure_conn.close()


if __name__ == "__main__":
    main()