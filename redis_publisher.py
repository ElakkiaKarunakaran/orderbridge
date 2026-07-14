import redis
import json
import sqlite3
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def publish_events():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute("SELECT order_id, domain, event_type, timestamp FROM order_events")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        event = {
            "order_id": row[0],
            "domain": row[1],
            "event_type": row[2],
            "timestamp": row[3]
        }
        r.publish('order_events', json.dumps(event))
        print(f"Published: {event['domain']} | Order {event['order_id']} | {event['event_type']}")
        time.sleep(0.3)

    print(f"\nDone — published {len(rows)} events to Redis channel: order_events")

if __name__ == '__main__':
    publish_events()