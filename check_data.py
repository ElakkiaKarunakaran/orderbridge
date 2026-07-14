import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect("orders.db")

# Read order_events table
df = pd.read_sql_query("SELECT * FROM order_events", conn)

conn.close()

# Display columns
print("Columns available:")
print(df.columns.tolist())

print("\nSample order data:")
print(df.head(10))
