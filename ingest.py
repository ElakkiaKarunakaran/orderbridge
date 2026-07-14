import requests
import sqlite3
import redis
import json

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

conn = sqlite3.connect('orders.db')

# Shared event schema table (matches proposal's normalized format)
conn.execute('''CREATE TABLE IF NOT EXISTS order_events 
    (order_id INTEGER, domain TEXT, event_type TEXT, timestamp TEXT)''')

# Domain 1: Order capture (CRM mock)
crm_data = requests.get('http://localhost:3000/orders').json()
for o in crm_data:

    event = {
        "order_id": o['id'],
        "domain": "order_capture",
        "event_type": o['status'],
        "timestamp": o['timestamp']
    }


    conn.execute(
        'INSERT INTO order_events VALUES (?,?,?,?)',
        (
            event["order_id"],
            event["domain"],
            event["event_type"],
            event["timestamp"]
        )
    )


    redis_client.publish(
        "orders",
        json.dumps(event)
    )

# Domain 2: Fulfilment mock
fulfilment_data = requests.get('http://localhost:4000/fulfilment').json()
for f in fulfilment_data:

    event = {
        "order_id": f['order_id'],
        "domain": f['domain'],
        "event_type": f['event_type'],
        "timestamp": f['timestamp']
    }


    conn.execute(
        'INSERT INTO order_events VALUES (?,?,?,?)',
        (
            event["order_id"],
            event["domain"],
            event["event_type"],
            event["timestamp"]
        )
    )


    redis_client.publish(
        "orders",
        json.dumps(event)
    )

# Domain 3: Logistics mock
logistics_data = requests.get('http://localhost:5000/logistics').json()
for l in logistics_data:

    event = {
        "order_id": l['order_id'],
        "domain": l['domain'],
        "event_type": l['event_type'],
        "timestamp": l['timestamp']
    }


    conn.execute(
        'INSERT INTO order_events VALUES (?,?,?,?)',
        (
            event["order_id"],
            event["domain"],
            event["event_type"],
            event["timestamp"]
        )
    )


    redis_client.publish(
        "orders",
        json.dumps(event)
    )

conn.commit()
conn.close()
print("Ingested", len(crm_data) + len(fulfilment_data) + len(logistics_data), "events from 3 domains into shared schema")