import requests
from icalendar import Calendar
from datetime import datetime
from django.core.cache import cache

CACHE_TIMEOUT = 60 * 30  # 30 minuti


def get_booking_events(url):
    cache_key = f"ical_{url}"

    events = cache.get(cache_key)
    if events:
        return events

    resp = requests.get(url)
    events = []

    if resp.status_code == 200:
        cal = Calendar.from_ical(resp.text)

        for event in cal.walk("VEVENT"):
            start = event.get("DTSTART").dt
            end = event.get("DTEND").dt

            events.append({
                "start": start,
                "end": end
            })

    cache.set(cache_key, events, CACHE_TIMEOUT)

    return events