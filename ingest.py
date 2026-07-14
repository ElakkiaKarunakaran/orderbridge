import requests
import sqlite3

conn = sqlite3.connect('orders.db')

# Shared event schema table (matches proposal's normalized format)
conn.execute('''CREATE TABLE IF NOT EXISTS order_events 
    (order_id INTEGER, domain TEXT, event_type TEXT, timestamp TEXT)''')

# Domain 1: Order capture (CRM mock)
crm_data = requests.get('http://localhost:3000/orders').json()
for o in crm_data:
    conn.execute('INSERT INTO order_events VALUES (?,?,?,?)',
        (o['id'], 'order_capture', o['status'], o['timestamp']))

# Domain 2: Fulfilment mock
fulfilment_data = requests.get('http://localhost:4000/fulfilment').json()
for f in fulfilment_data:
    conn.execute('INSERT INTO order_events VALUES (?,?,?,?)',
        (f['order_id'], f['domain'], f['event_type'], f['timestamp']))

# Domain 3: Logistics mock
logistics_data = requests.get('http://localhost:5000/logistics').json()
for l in logistics_data:
    conn.execute('INSERT INTO order_events VALUES (?,?,?,?)',
        (l['order_id'], l['domain'], l['event_type'], l['timestamp']))

conn.commit()
conn.close()
print("Ingested", len(crm_data) + len(fulfilment_data) + len(logistics_data), "events from 3 domains into shared schema")