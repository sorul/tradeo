"""Script to collect different utilities."""
from datetime import datetime
from .config import Config


def stringToDateUTC(
    str_date,
    format='%Y.%m.%d %H:%M',
    timezone=Config.utc_timezone
) -> datetime:
  """Convert a string to a datetime object."""
  r = timezone.localize(datetime.strptime(str_date, format))
  return r.astimezone(Config.utc_timezone)
