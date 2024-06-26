import pytest
from datetime import datetime
import tradeo.utils as utils
import pytz
from tradeo.files import try_read_file
from tradeo.files import Files
from unittest.mock import patch


def test_basic():
  str_date = '2023.01.01 12:00'
  expected = datetime(2023, 1, 1, 12, 0, tzinfo=pytz.utc)
  result = utils.string_to_date_utc(str_date)
  assert result == expected


def test_different_format():
  str_date = '01/01/2023 12:00 PM'
  expected = datetime(2023, 1, 1, 12, 0, tzinfo=pytz.utc)
  result = utils.string_to_date_utc(str_date, '%m/%d/%Y %I:%M %p')
  assert result == expected


def test_timezone():
  str_date = '2023.01.01 12:00'
  ny_timezone = pytz.timezone('America/New_York')
  expected = datetime(2023, 1, 1, 17, 0, tzinfo=pytz.utc)
  result = utils.string_to_date_utc(str_date, from_timezone=ny_timezone)
  assert result == expected


def test_invalid_date():
  str_date = 'invalid'
  with pytest.raises(ValueError, match='does not match format'):
    utils.string_to_date_utc(str_date)


@patch('tradeo.files.get_default_path')
def test_reset_consecutive_times_down(mock_default_path, tmp_path):

  # Make data_path() return the temporary directory
  mock_default_path.return_value = tmp_path

  # Create the file with some content
  mock_text = '10'
  file_path = tmp_path / Files.CONSECUTIVE_TIMES_DOWN.value
  with open(file_path, 'w') as file:
    file.write(mock_text)

  assert try_read_file(file_path) == mock_text

  # Call to the function to test
  utils.reset_consecutive_times_down()

  assert try_read_file(file_path) == '0'


@patch('tradeo.utils.get_default_path')
def test_get_last_balance(mock_default_path, tmp_path):

  # Make data_path() return the temporary directory
  mock_default_path.return_value = tmp_path

  # Create the file with some content
  with open(tmp_path / Files.LAST_BALANCE.value, 'w') as file:
    file.write('100')

  # Call to the function to test
  assert utils.get_last_balance() == 100


@patch('tradeo.utils.get_default_path')
def test_get_consecutive_times_down(mock_default_path, tmp_path):

  # Make data_path() return the temporary directory
  mock_default_path.return_value = tmp_path

  # Create the file with some content
  with open(tmp_path / Files.CONSECUTIVE_TIMES_DOWN.value, 'w') as file:
    file.write('10')

  # Call to the function to test
  assert utils.get_consecutive_times_down() == 10


@patch('tradeo.utils.get_default_path')
@patch('tradeo.files.get_default_path')
def test_increment_consecutive_times_down(
        mock_default_utils_path, mock_default_files_path, tmp_path):

  mock_default_utils_path.return_value = tmp_path
  mock_default_files_path.return_value = tmp_path

  # Create the CONSECUTIVE_TIMES_DOWN file with some content
  with open(tmp_path / Files.CONSECUTIVE_TIMES_DOWN.value, 'w') as file:
    file.write('10')

  # Call to the function to test
  utils.increment_consecutive_times_down()

  assert utils.get_consecutive_times_down() == 11
