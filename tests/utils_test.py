import pytest
from datetime import datetime
import tradingbot.utils as utils
from tradingbot.config import Config
import pytz
from tradingbot.files import Files as f
from unittest.mock import patch


def test_basic():
  str_date = '2023.01.01 12:00'
  expected = datetime(2023, 1, 1, 12, 0, tzinfo=pytz.utc)
  result = utils.stringToDateUTC(str_date)
  assert result == expected


def test_different_format():
  str_date = '01/01/2023 12:00 PM'
  expected = datetime(2023, 1, 1, 12, 0, tzinfo=pytz.utc)
  result = utils.stringToDateUTC(str_date, '%m/%d/%Y %I:%M %p')
  assert result == expected


def test_timezone():
  str_date = '2023.01.01 12:00'
  ny_timezone = pytz.timezone('America/New_York')
  expected = datetime(2023, 1, 1, 17, 0, tzinfo=pytz.utc)
  result = utils.stringToDateUTC(str_date, timezone=ny_timezone)
  assert result == expected


def test_invalid_date():
  str_date = 'invalid'
  with pytest.raises(ValueError, match='does not match format'):
    utils.stringToDateUTC(str_date)


def test_get_script_name():
  expected = 'utils'
  result = utils.get_script_name()
  assert result == expected


@patch('tradingbot.utils.data_path')
def test_get_successful_symbols(mock_data_path, tmp_path):

  # Make data_path() return the temporary directory
  mock_data_path.return_value = tmp_path

  with open(tmp_path / f.SUCCESSFUL_SYMBOLS.value, 'w') as file:
    file.write('EURUSD\nUSDJPY\nGBPUSD')

  result = utils.get_successful_symbols()
  assert result == ['EURUSD', 'USDJPY', 'GBPUSD']


@patch('tradingbot.utils.data_path')
def test_get_remaining_symbols(mock_data_path, tmp_path):

  # Make data_path() return the temporary directory
  mock_data_path.return_value = tmp_path

  with open(tmp_path / f.SUCCESSFUL_SYMBOLS.value, 'w') as file:
    file.write('EURUSD\nUSDJPY\nGBPUSD')

  result = utils.get_remaining_symbols()
  assert len(result) == len(Config.symbols) - 3
  assert 'EURUSD' not in result
