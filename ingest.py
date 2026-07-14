import requests
import sqlite3

# Connect to (or create) the database file
conn = sqlite3.connect('orders.db')
conn.execute('''CREATE TABLE IF NOT EXISTS orders 
    (id INTEGER, customer TEXT, status TEXT, timestamp TEXT)''')

# Pull data from the mock CRM
response = requests.get('http://localhost:3000/orders')
data = response.json()

# Insert each order into the database
for o in data:
    conn.execute('INSERT INTO orders VALUES (?,?,?,?)', 
        (o['id'], o['customer'], o['status'], o['timestamp']))

conn.commit()
conn.close()
print("Ingested", len(data), "orders into SQLite")