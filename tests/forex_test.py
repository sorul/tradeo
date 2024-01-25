from tradingbot.forex import is_locked, check_time_viability
from tradingbot.files import Files
from freezegun import freeze_time
from datetime import datetime
from pathlib import Path
from tradingbot.config import Config
from unittest.mock import patch
import pytz


@patch('tradingbot.files.data_path')
def test_is_locked(mock_data_path, tmp_path):

  # Make data_path() return the temporary directory
  mock_data_path.return_value = tmp_path

  lock_file = Path(tmp_path / Files.FOREX_LOCK.value)
  lock_file.touch()

  assert is_locked()

  # Test when lock file does not exist
  lock_file.unlink()
  assert not is_locked()


def test_check_time_viability():
  tz = pytz.timezone(str(Config.broker_timezone))

  # Correct
  d = datetime(2024, 1, 9, 12, 5)
  with freeze_time(tz.localize(d)):
    assert check_time_viability()

  # Weekday
  d = datetime(2024, 1, 27, 12, 5)
  with freeze_time(tz.localize(d)):
    assert not check_time_viability()

  # 0 minutes
  d = datetime(2024, 1, 14, 12, 0)
  with freeze_time(tz.localize(d)):
    assert not check_time_viability()

  # Friday after 00:00
  d = datetime(2024, 1, 27, 00, 5)
  with freeze_time(tz.localize(d)):
    assert not check_time_viability()

  # Sunday before 00:00
  d = datetime(2024, 1, 28, 23, 55)
  with freeze_time(tz.localize(d)):
    assert not check_time_viability()
