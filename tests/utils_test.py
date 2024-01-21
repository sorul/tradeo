import pytest
from datetime import datetime
from tradingbot.utils import stringToDateUTC
import pytz


def test_basic():
  str_date = '2023.01.01 12:00'
  expected = datetime(2023, 1, 1, 12, 0, tzinfo=pytz.utc)
  result = stringToDateUTC(str_date)
  assert result == expected


def test_different_format():
  str_date = '01/01/2023 12:00 PM'
  expected = datetime(2023, 1, 1, 12, 0, tzinfo=pytz.utc)
  result = stringToDateUTC(str_date, '%m/%d/%Y %I:%M %p')
  assert result == expected


def test_timezone():
  str_date = '2023.01.01 12:00'
  ny_timezone = pytz.timezone('America/New_York')
  expected = datetime(2023, 1, 1, 17, 0, tzinfo=pytz.utc)
  result = stringToDateUTC(str_date, timezone=ny_timezone)
  assert result == expected


def test_invalid_date():
  str_date = 'invalid'
  with pytest.raises(ValueError):
    stringToDateUTC(str_date)
