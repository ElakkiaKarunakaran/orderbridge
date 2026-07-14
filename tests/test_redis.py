import redis
import json
import threading
import time

def test_redis_connection():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    assert r.ping() == True

def test_publish_and_receive():
    r_pub = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r_sub = redis.Redis(host='localhost', port=6379, decode_responses=True)

    pubsub = r_sub.pubsub()
    pubsub.subscribe('test_channel')

    received = []

    def listen():
        for message in pubsub.listen():
            if message['type'] == 'message':
                received.append(json.loads(message['data']))
                break

    thread = threading.Thread(target=listen)
    thread.start()

    time.sleep(0.5)

    test_event = {
        "order_id": 99,
        "domain": "order_capture",
        "event_type": "placed",
        "timestamp": "2026-07-14T10:00:00Z"
    }
    r_pub.publish('test_channel', json.dumps(test_event))

    thread.join(timeout=3)

    assert len(received) == 1
    assert received[0]['order_id'] == 99
    assert received[0]['domain'] == 'order_capture'