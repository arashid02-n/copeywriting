import os
from posthog import Posthog

# Load from environment
POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY", "YOUR_API_KEY_HERE")
POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://us.posthog.com")  # <-- اصلاح شد

# Correct initialization
ph = Posthog(
    POSTHOG_API_KEY,
    host=POSTHOG_HOST
)

def track_event(user_id: str, event_name: str, properties: dict = None):
    """
    Send an event to PostHog
    """
    if properties is None:
        properties = {}

    ph.capture(
        distinct_id=user_id,
        event=event_name,
        properties=properties
    )

