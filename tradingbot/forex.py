"""Script to handle the forex bot."""
from datetime import datetime
from .config import Config
from .files import file_exists


def main():
  """Execute forex bot."""
  pass


def check_time_viability() -> bool:
  """Check if the forex bot is viable to run."""
  now_date = datetime.now(Config.forex_timezone)
  # Monday (0) - Sunday (6)
  is_weekday = now_date.weekday() in [0, 1, 2, 3]
  is_friday = now_date.weekday() == 4 and now_date.hour < 17
  is_sunday = now_date.weekday() == 6 and now_date.hour >= 17
  # TODO: When executions are performed with the real account,
  # we need to consider testing the removal of this condition.
  is_not_on_the_hour = now_date.minute != 0
  return (
      is_not_on_the_hour
      and (
          is_weekday
          or is_friday
          or is_sunday
      )
  )


def handle():
  """Handle the forex bot."""
  if not is_locked() and check_time_viability():
    main()


def is_locked() -> bool:
  """Return True if the forex-bot is running."""
  return file_exists('forex_lock')
