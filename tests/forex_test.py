from tradingbot.forex import is_locked, check_time_viability
from tradingbot.files import Files
from tradingbot.forex import _send_profit_message
from freezegun import freeze_time
from datetime import datetime
from pathlib import Path
from tradingbot.config import Config
from unittest.mock import patch
from tradingbot.forex_client import MT_Client
import pytz


@patch('tradingbot.files.get_default_path')
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


@patch('tradingbot.files.get_default_path')
def test_send_profit_message(mock_data_path, tmp_path):
  tz = pytz.timezone(str(Config.local_timezone))
  mt_client = MT_Client()
  mt_client.account_info = {'balance': 100.0}

  # Make data_path() return the temporary directory
  mock_data_path.return_value = tmp_path

  # Create the file with some content
  with open(tmp_path / Files.LAST_BALANCE.value, 'w') as file:
    file.write('20')

  # Sends a message
  d = datetime(2024, 1, 1, 12, 5)
  assert _send_profit_message(tz.localize(d))

  # Doesn't send a message
  d = datetime(2024, 1, 1, 13, 5)
  assert not _send_profit_message(tz.localize(d))
