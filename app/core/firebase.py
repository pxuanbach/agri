from firebase_admin import messaging

class FireBase():

    def __init__(self) -> None:
        pass

    def subscribe(self, **kwargs):
        """
            Multiple tokens subscribe multiple topics
        """
        print("subscribe", kwargs)
        tokens = kwargs.get("tokens", [])
        topics = kwargs.get("topics", [])
        try:
            for topic in topics:
                response = messaging.subscribe_to_topic(tokens, topic)
                if response.failure_count > 0:
                    print(
                        f"Failed to subscribe to topic {topic} due to {list(map(lambda e: e.reason,response.errors))}")
        except Exception as e:
            print(e)
    def unsubscribe(self, **kwargs):
        """
            Multiple tokens unsubscribe multiple topics
        """
        print("unsubscribe", kwargs)
        tokens = kwargs.get("tokens", [])
        topics = kwargs.get("topics", [])
        try:
            for topic in topics:
                response = messaging.unsubscribe_from_topic(tokens, topic)
                if response.failure_count > 0:
                    print(
                        f"Failed to unsubscribe from topic {topic} due to {list(map(lambda e: e.reason,response.errors))}")
        except Exception as e:
            print(e)
    def send_to_topics(self, **kwargs):
        """
            Send to multiple topics  
            **kwargs:  
                - title: Title
                - body: Content
                - data: Dict of data
                - topics: Dict of data
        """
        print("send_to_topics", kwargs)
        title = kwargs.get("title", "")
        body = kwargs.get("body", "")
        data = kwargs.get("data", {})
        topics = kwargs.get("topics", [])
        try:
            for topic in topics:
                message = messaging.Message(
                    data=data,
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    topic=topic,
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(aps=messaging.Aps(content_available=True))
                    ),
                    android=messaging.AndroidConfig(
                        priority="high",
                        notification=messaging.AndroidNotification(
                            priority="max", 
                            # channel_id="high_importance_channel"
                        )
                    )
                )
                messaging.send(message)
        except Exception as e:
            print(e)

    def send_to_tokens(self, **kwargs):
        data = kwargs.get("data", {})
        title = kwargs.get("title", "")
        body = kwargs.get("body", "")
        tokens = kwargs.get("tokens", [])
        message = messaging.MulticastMessage(
            data=data,
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            tokens=tokens
        )
        messaging.send_multicast(message)

    def send_to_token(self, **kwargs):
        title = kwargs.get("title", "")
        body = kwargs.get("body", "")
        token = kwargs.get("token", "")
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token
        )
        messaging.send(message)
_firebase = FireBase()
