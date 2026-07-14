import redis
import json
import pandas as pd
from sklearn.ensemble import IsolationForest


# Connect to Redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


# Subscribe to orders channel

subscriber = redis_client.pubsub()

subscriber.subscribe("orders")


print("Listening for live order events...")


events = []


while True:

    message = subscriber.get_message(
        ignore_subscribe_messages=True,
        timeout=1
    )


    if message:

        order_event = json.loads(message["data"])


        print("\nReceived Event:")
        print(order_event)


        events.append(order_event)


        # Convert events into dataframe

        df = pd.DataFrame(events)


        # Count events per order

        event_count = (
            df.groupby("order_id")
            .size()
            .reset_index(name="event_count")
        )


        # Need minimum data points

        if len(event_count) >= 3:


            model = IsolationForest(
                contamination=0.1,
                random_state=42
            )


            model.fit(
                event_count[["event_count"]]
            )


            event_count["result"] = model.predict(
                event_count[["event_count"]]
            )


            latest = event_count.iloc[-1]


            if latest["result"] == -1:

                print(
                    "🚨 ANOMALY DETECTED FOR ORDER:",
                    latest["order_id"]
                )

            else:

                print(
                    "✅ Normal Order:",
                    latest["order_id"]
                )