from posthog import Posthog

# --- Correct PostHog settings ---
POSTHOG_API_KEY = "phc_9LhkwALp1yKFMroS5JzNMXe7OvkmO4LdepFj5m6zX1X"
POSTHOG_HOST = "https://us.i.posthog.com"   # Correct endpoint!

# Initialize client
ph = Posthog(
    POSTHOG_API_KEY,
    host=POSTHOG_HOST
)

def track_event(user_id: str, event_name: str, properties: dict = None):
    if properties is None:
        properties = {}

    try:
        ph.capture(
            distinct_id=str(user_id),
            event=event_name,
            properties=properties
        )
    except Exception as e:
        print("PostHog Error:", e)
