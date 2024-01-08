from tradingbot.forex import is_locked, check_time_viability
from tradingbot.paths import config_path
from freezegun import freeze_time
from datetime import datetime
from tradingbot.config import Config
import pytz


def test_is_locked():
  # Test when lock file exists
  lock_file = config_path() / 'forex_lock'
  lock_file.touch()
  assert is_locked()

  # Test when lock file does not exist
  lock_file.unlink()
  assert not is_locked()


def test_check_time_viability():
  tz = pytz.timezone(str(Config.forex_timezone))

  # Correct
  d = datetime(2024, 1, 9, 12, 5)
  with freeze_time(tz.localize(d)):
    assert check_time_viability()

  # Weekday
  d = datetime(2024, 1, 14, 12, 5)
  with freeze_time(tz.localize(d)):
    assert not check_time_viability()

  # 0 minutes
  d = datetime(2024, 1, 14, 12, 0)
  with freeze_time(tz.localize(d)):
    assert not check_time_viability()

  # Friday after 17:00
  d = datetime(2024, 1, 12, 17, 5)
  with freeze_time(tz.localize(d)):
    assert not check_time_viability()

  # Sunday before 17:00
  d = datetime(2024, 1, 14, 16, 5)
  with freeze_time(tz.localize(d)):
    assert not check_time_viability()
