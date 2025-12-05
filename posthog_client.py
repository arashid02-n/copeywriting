from posthog import Posthog

# --- PostHog configuration ---
POSTHOG_API_KEY = "phc_9LhkwALp1yKFMroS5JzNMXe7OvkmO4LdepFj5m6zX1X"
POSTHOG_HOST = "https://us.i.posthog.com"  # Correct endpoint

# Initialize client
ph = Posthog(
    project_api_key=POSTHOG_API_KEY,
    host=POSTHOG_HOST
)

def track_event(user_id: str, event_name: str, properties: dict = None):
    """
    Send an event to PostHog.
    user_id: any string that identifies the user (e.g. email, username)
    event_name: the event name you want to track
    properties: optional dict with extra info
    """
    if properties is None:
        properties = {}

    try:
        ph.capture(
            distinct_id=str(user_id),
            event=event_name,
            properties=properties
        )
        print(f"✅ Event '{event_name}' sent for user '{user_id}'")
    except Exception as e:
        print("❌ PostHog Error:", e)
