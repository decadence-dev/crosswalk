from datetime import datetime

import pytz


def astimezone(date: datetime, timezone: str = "UTC"):
    timezone = pytz.timezone(timezone)
    return date.astimezone(timezone) if date is not None else None
