import time
from collections import deque

MAX_REQUESTS_PER_MINUTE = 5
MAX_REQUESTS_PER_DAY = 200
COOLDOWN_SECONDS = 10

requests_minute = deque()
requests_day = deque()
last_call_time = 0

def check_rate_limit():
    global last_call_time
    now = time.time()

    if now - last_call_time < COOLDOWN_SECONDS:
        remaining = COOLDOWN_SECONDS - (now - last_call_time)
        return False, f"Cooldown active. Try in {remaining:.1f}s"

    while requests_minute and now - requests_minute[0] > 60:
        requests_minute.popleft()

    while requests_day and now - requests_day[0] > 86400:
        requests_day.popleft()

    if len(requests_minute) >= MAX_REQUESTS_PER_MINUTE:
        return False, "Too many requests this minute."

    if len(requests_day) >= MAX_REQUESTS_PER_DAY:
        return False, "Daily request limit reached."

    requests_minute.append(now)
    requests_day.append(now)
    last_call_time = now

    return True, None
