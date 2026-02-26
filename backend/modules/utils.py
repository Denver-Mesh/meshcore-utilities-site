import time
from datetime import datetime, timedelta


def now() -> datetime:
    """
    Get the current date and time as a datetime object.
    :return: The current date and time.
    """
    return datetime.now()


def now_delta(days: int = 0, hours: int = 0, minutes: int = 0) -> datetime:
    """
    Get the current date and time with a specified delta.
    :param days: The number of days to add (or subtract if negative).
    :param hours: The number of hours to add (or subtract if negative).
    :param minutes: The number of minutes to add (or subtract if negative).
    :return: The current date and time with the specified delta applied.
    """
    return datetime.now() + timedelta(days=days, hours=hours, minutes=minutes)


def timestamp_within_delta(timestamp: int, days: int = 0, hours: int = 0, minutes: int = 0) -> bool:
    """
    Check if a given timestamp is within a specified delta from the current time.
    :param timestamp: The timestamp to check (in seconds since the epoch).
    :param days: The number of days for the delta.
    :param hours: The number of hours for the delta.
    :param minutes: The number of minutes for the delta.
    :return: True if the timestamp is within the specified delta from now, False otherwise.
    """
    if not timestamp:
        return False

    target_time = datetime.fromtimestamp(timestamp)
    now_time = datetime.now()
    delta = timedelta(days=days, hours=hours, minutes=minutes)
    if target_time > now_time:  # Dealing with positive deltas (future timestamps)
        return target_time - now_time <= delta
    else:
        return now_time - target_time <= delta


def iso8601_to_unix_timestamp(iso_str: str) -> int:
    if not iso_str:
        return 0

    try:
        # e.g. 2026-02-18T01:19:00.379Z
        dt = time.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        return int(time.mktime(dt))
    except Exception as e:
        return 0


def epoch_to_date(epoch_time: int) -> str:
    """Convert epoch timestamp to YYYY-MM-DD format."""
    if not epoch_time:
        return "N/A"

    try:
        # Convert epoch to datetime and format as YYYY-MM-DD
        dt = datetime.fromtimestamp(int(epoch_time))
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return "Invalid date"

def epoch_to_datetime(epoch_time: int) -> str:
    """Convert epoch timestamp to YYYY-MM-DD HH:MM:SS format."""
    if not epoch_time:
        return "N/A"

    try:
        # Convert epoch to datetime and format as YYYY-MM-DD HH:MM:SS
        dt = datetime.fromtimestamp(int(epoch_time))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return "Invalid date"
