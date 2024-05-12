import pytz
from freezegun import freeze_time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
import shutil

from tradeo.paths import resources_test_path
from tradeo.executable.basic_forex import BasicForex
from tradeo.files import Files
from tradeo.config import Config
from tradeo.mt_client import MT_Client


@patch('tradeo.files.get_default_path')
def test_is_locked(mock_data_path, tmp_path):

  # Make data_path() return the temporary directory
  mock_data_path.return_value = tmp_path

  bf = BasicForex()
  lock_file = Path(tmp_path / f'{bf.name}.block')
  lock_file.touch()

  assert bf.is_locked()

  # Test when lock file does not exist
  lock_file.unlink()
  assert not bf.is_locked()


def test_check_time_viability():
  tz = pytz.timezone(str(Config.broker_timezone))
  bf = BasicForex()

  # Correct
  d = datetime(2024, 1, 9, 12, 5)
  with freeze_time(tz.localize(d)):
    assert bf.check_time_viability()

  # Weekday
  d = datetime(2024, 1, 27, 12, 5)
  with freeze_time(tz.localize(d)):
    assert not bf.check_time_viability()

  # 0 minutes
  d = datetime(2024, 1, 14, 12, 0)
  with freeze_time(tz.localize(d)):
    assert not bf.check_time_viability()

  # Friday after 00:00
  d = datetime(2024, 1, 27, 00, 5)
  with freeze_time(tz.localize(d)):
    assert not bf.check_time_viability()

  # Sunday before 00:00
  d = datetime(2024, 1, 28, 23, 55)
  with freeze_time(tz.localize(d)):
    assert not bf.check_time_viability()


@patch('tradeo.files.get_default_path')
def test_send_profit_message(mock_data_path, tmp_path):
  # Copy the Orders.json file to the temporary folder
  orders_path = tmp_path / 'Orders.json'
  original_orders_path = Path(
      f'{resources_test_path()}/AgentFiles/Orders.json')
  shutil.copyfile(original_orders_path, orders_path)

  # Copy the Orders_Stored.json file to the temporary folder
  orders_stored_path = tmp_path / 'Orders_Stored.json'
  original_orders_stored_path = Path(
      f'{resources_test_path()}/AgentFiles/Orders_Stored.json')
  shutil.copyfile(original_orders_stored_path, orders_stored_path)

  mt_client = MT_Client()
  mt_client.path_orders = orders_path
  mt_client.path_orders_stored = orders_stored_path
  mt_client.account_info = {'balance': 100.0}

  tz = pytz.timezone(str(Config.local_timezone))
  bf = BasicForex()

  # Make data_path() return the temporary directory
  mock_data_path.return_value = tmp_path

  # Create the file with some content
  with open(tmp_path / Files.LAST_BALANCE.value, 'w') as file:
    file.write('20')

  # Sends a message
  d = datetime(2024, 1, 1, 12, 5)
  assert bf._send_profit_message(mt_client, tz.localize(d))

  # Doesn't send a message
  d = datetime(2024, 1, 1, 13, 5)
  assert not bf._send_profit_message(mt_client, tz.localize(d))


@patch('tradeo.files.get_default_path')
@patch('tradeo.mt_client.MT_Client.get_remaining_symbols')
def test_handle_new_historical_data(
        mock_remaining_symbols, mock_data_path, tmp_path):
  mock_data_path.return_value = tmp_path
  Config.mt_files_path = tmp_path
  mt_client = MT_Client()

  mock_remaining_symbols.return_value = []
  bf = BasicForex()
  bf.handle_new_historical_data(
      mt_client, datetime.now(Config.utc_timezone), timedelta(seconds=0)
  )


@patch('tradeo.mt_client.Config')
def test_handle_trades(mock_config, tmp_path):
  # Copy the Orders.json file to the temporary folder
  orders_path = tmp_path / 'Orders.json'
  original_orders_path = Path(
      f'{resources_test_path()}/AgentFiles/Orders.json')
  shutil.copyfile(original_orders_path, orders_path)

  # Copy the Orders_Stored.json file to the temporary folder
  orders_stored_path = tmp_path / 'Orders_Stored.json'
  original_orders_stored_path = Path(
      f'{resources_test_path()}/AgentFiles/Orders_Stored.json')
  shutil.copyfile(original_orders_stored_path, orders_stored_path)

  mock_config.mt_files_path = tmp_path
  mock_config.utc_timezone = pytz.utc
  mt_client = MT_Client()
  mt_client.path_orders = orders_path
  mt_client.path_orders_stored = orders_stored_path
  Path(tmp_path / 'AgentFiles').mkdir(exist_ok=True)
  mt_client.path_commands_prefix = tmp_path / 'AgentFiles/Commands_'

  bf = BasicForex()
  bf.handle_trades(mt_client)


@patch('tradeo.files.get_default_path')
def test_check_mt_needs_to_restart(mock_data_path, tmp_path):
  mock_data_path.return_value = tmp_path
  bf = BasicForex()
  bf._check_mt_needs_to_restart(1)


@patch('tradeo.files.get_default_path')
@patch('tradeo.mt_client.MT_Client.get_remaining_symbols')
def test_main(mock_remaining_symbols, mock_data_path, tmp_path):
  # Copy the Orders.json file to the temporary folder
  orders_path = tmp_path / 'Orders.json'
  original_orders_path = Path(
      f'{resources_test_path()}/AgentFiles/Orders.json')
  shutil.copyfile(original_orders_path, orders_path)

  # Copy the Orders_Stored.json file to the temporary folder
  orders_stored_path = tmp_path / 'Orders_Stored.json'
  original_orders_stored_path = Path(
      f'{resources_test_path()}/AgentFiles/Orders_Stored.json')
  shutil.copyfile(original_orders_stored_path, orders_stored_path)

  Config.mt_files_path = tmp_path
  mt_client = MT_Client()
  mt_client.path_orders = orders_path
  mt_client.path_orders_stored = orders_stored_path
  Path(tmp_path / 'AgentFiles').mkdir(exist_ok=True)
  mt_client.path_commands_prefix = tmp_path / 'AgentFiles/Commands_'
  mt_client.path_historical_data_prefix = Path(
      tmp_path / 'AgentFiles/Historical_Data_'
  )
  mt_client.path_messages = Path(
      tmp_path / 'AgentFiles/Messages.json'
  )

  mock_data_path.return_value = tmp_path
  mock_remaining_symbols.return_value = []
  bf = BasicForex()
  bf.main(mt_client)
