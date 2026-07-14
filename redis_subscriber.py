import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
pubsub = r.pubsub()
pubsub.subscribe('order_events')

print("Listening on channel: order_events")
print("Waiting for messages...\n")

for message in pubsub.listen():
    if message['type'] == 'message':
        event = json.loads(message['data'])
        print(f"RECEIVED → Order {event['order_id']} | {event['domain']} | {event['event_type']} | {event['timestamp']}")