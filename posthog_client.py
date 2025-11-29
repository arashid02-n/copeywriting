# posthog_client.py
from posthog import Posthog
import os

POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY", "ae3f6f4f32655b49246bb473863a9d19f2a05f28dcbf274951e37c02198cba51")
POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://copey.rashidnazari.com")

ph = Posthog(
    api_key=POSTHOG_API_KEY,
    host=POSTHOG_HOST,
    send=True  # immediately send events
)

def track_event(user_id: str, event_name: str, properties: dict = None):
    """
    Send an event to PostHog
    :param user_id: string, unique identifier for the user
    :param event_name: string, name of the event
    :param properties: optional dict with additional info
    """
    if properties is None:
        properties = {}
    ph.capture(
        distinct_id=user_id,
        event=event_name,
        properties=properties
    )
