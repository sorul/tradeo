from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from tradingbot.forex_client import MT_Client
from tradingbot.config import Config
import shutil
from pandas import DataFrame
from tradingbot.files import try_load_json, try_read_file
import json
from datetime import datetime
import pytz
from freezegun import freeze_time
from tradingbot.paths import test_resources
from os.path import join


def test_set_agent_paths():
  mock_config = MagicMock()
  mock_config.mt_files_path = test_resources()

  with patch('tradingbot.forex_client.Config', mock_config):
    client = MT_Client()
    path_file = join(mock_config.mt_files_path, client.prefix_files_path)

    # Method to test
    client.set_agent_paths()

    assert client.path_orders == Path(join(path_file, 'Orders.json'))
    assert client.path_messages == Path(join(path_file, 'Messages.json'))
    assert client.path_market_data == Path(join(path_file, 'Market_Data.json'))
    assert client.path_bar_data == Path(join(path_file, 'Bar_Data.json'))
    assert client.path_historic_data == Path(join(path_file))
    assert client.path_historic_trades == Path(join(
        path_file, 'Historic_Trades.json'))
    assert client.path_orders_stored == Path(join(
        path_file, 'Orders_Stored.json'))
    assert client.path_messages_stored == Path(join(
        path_file, 'Messages_Stored.json'))
    assert client.path_commands_prefix == Path(join(path_file, 'Commands_'))


def test_set_agent_paths_missing_dir():
  original_mt_path = Config.mt_files_path
  Config.mt_files_path = Path('invalid/path')
  with pytest.raises(SystemExit):
    client = MT_Client()
    client.set_agent_paths()
  Config.mt_files_path = original_mt_path


def test_check_messages(tmp_path):

  # Copy the Messages.json file to the temporary folder
  messages_path = tmp_path / 'Messages.json'
  original_messages_path = Path(f'{test_resources()}/Messages.json')
  shutil.copyfile(original_messages_path, messages_path)

  client = MT_Client()
  client.path_messages = messages_path

  # Call for the first time to read messages
  client.check_messages()

  assert_data = {
      'INFO': [['2024.01.18 22:26:36', 'Dummy Info']],
      'ERROR': [['2024.01.18 22:26:36', 'Dummy Error']]
  }
  assert client.messages == assert_data

  # Does not change on second call
  client.check_messages()

  assert client.messages == assert_data

  # Write new message
  data = try_load_json(messages_path)
  data['33333333'] = {
      'type': 'INFO', 'time': '2024.01.18 22:26:36', 'message': 'New Message'
  }
  with open(messages_path, 'w') as f:
    f.write(json.dumps(data))

  # Now it does change
  client.check_messages()

  assert_data['INFO'].append(['2024.01.18 22:26:36', 'New Message'])
  assert client.messages == assert_data


def test_check_market_data(tmp_path):

  # Copy the Market_Data.json file to the temporary folder
  market_data_path = tmp_path / 'Market_Data.json'
  original_market_data_path = Path(f'{test_resources()}/Market_Data.json')
  shutil.copyfile(original_market_data_path, market_data_path)

  client = MT_Client()
  client.path_market_data = market_data_path

  # Call for the first time to read data
  client.check_market_data()

  assert_data = {
      'EURUSD': {
          'bid': 1.08973,
          'ask': 1.08979,
          'tick_value': 0.91761
      },
      'EURGBP': {
          'bid': 0.85792,
          'ask': 0.85797,
          'tick_value': 1.16554
      }
  }
  assert client.market_data == assert_data

  # Does not change on second call
  client.check_market_data()

  assert client.market_data == assert_data

  # Write new data
  data = try_load_json(market_data_path)
  data['USDJPY'] = {
      'bid': 100,
      'ask': 100.5,
      'tick_value': 0.92
  }
  with open(market_data_path, 'w') as f:
    f.write(json.dumps(data))

  # Now it does change
  client.check_market_data()

  assert client.market_data == data


def test_check_bar_data(tmp_path):

  # Copy the Bar_Data.json file to the temporary folder
  bar_data_path = tmp_path / 'Bar_Data.json'
  original_bar_data_path = Path(f'{test_resources()}/Bar_Data.json')
  shutil.copyfile(original_bar_data_path, bar_data_path)

  client = MT_Client()
  client.path_bar_data = bar_data_path

  # Call for the first time to read data
  client.check_bar_data()

  assert_data = {
      'EURUSD_M1': {
          'open': [1.08973, 1.08975],
          'high': [1.08979, 1.08981],
          'low': [1.08967, 1.08969],
          'close': [1.08975, 1.08977]
      }
  }

  assert client.bar_data == assert_data

  # Does not change on second call
  client.check_bar_data()

  assert client.bar_data == assert_data

  # Write new data
  data = try_load_json(bar_data_path)
  data['EURUSD_M5'] = {
      'open': [1.08990, 1.08995],
      'high': [1.09000, 1.09005],
      'low': [1.08975, 1.08980],
      'close': [1.08995, 1.09000]
  }
  with open(bar_data_path, 'w') as f:
    f.write(json.dumps(data))

  # Now it does change
  client.check_bar_data()

  assert client.bar_data == data


def test_check_open_orders(tmp_path):

  # Copy the Orders.json file to the temporary folder
  orders_path = tmp_path / 'Orders.json'
  original_orders_path = Path(f'{test_resources()}/Orders.json')
  shutil.copyfile(original_orders_path, orders_path)

  # Copy the Orders_Stored.json file to the temporary folder
  orders_stored_path = tmp_path / 'Orders_Stored.json'
  original_orders_stored_path = Path(f'{test_resources()}/Orders_Stored.json')
  shutil.copyfile(original_orders_stored_path, orders_stored_path)

  client = MT_Client()
  client.path_orders = orders_path
  client.path_orders_stored = orders_stored_path

  # Call for the first time to read orders
  client.check_open_orders()

  assert_orders_data = {
      '2023993175': {
          'magic': 1705617043,
          'symbol': 'AUDUSD',
          'lots': 0.01,
          'type': 'buy',
          'open_price': 0.65754,
          'open_time': '2024.01.19 00:30:43',
          'SL': 0.65443,
          'TP': 0.0,
          'pnl': -0.59,
          'swap': 0.0,
          'comment': 'KAMIKAZE'
      }
  }
  assert_account_data = {
      'name': 'Foo',
      'number': -999999999,
      'currency': 'EUR',
      'leverage': 200,
      'free_margin': 999999.99,
      'balance': 999999.99,
      'equity': 999999.99
  }
  assert client.open_orders == assert_orders_data
  assert client.account_info == assert_account_data

  # Does not change on second call
  client.check_open_orders()

  assert client.open_orders == assert_orders_data
  assert client.account_info == assert_account_data

  # Write new data
  data = try_load_json(orders_path)
  data['orders']['2023993176'] = {
      'magic': 1705617044,
      'symbol': 'EURUSD',
      'lots': 0.02,
      'type': 'sell',
      'open_price': 1.5,
      'open_time': '2024.01.20 01:00:00',
      'SL': 1.6,
      'TP': 0.0,
      'pnl': 1.2,
      'swap': 0.001,
      'comment': 'NEW ORDER'
  }
  data['account_info']['name'] = 'Bar'
  data['account_info']['number'] = 123456789

  with open(orders_path, 'w') as f:
    f.write(json.dumps(data))

  # Now it changes
  client.check_open_orders()

  assert client.open_orders == data['orders']
  assert client.account_info == data['account_info']


def test_check_historic_data(tmp_path):

  symbol = 'USDJPY'

  # Create client
  client = MT_Client()
  client.path_historic_data = tmp_path
  client.path_historic_data = test_resources()

  data = client.check_historic_data(symbol)
  mock_data = {
      "USDJPY_M5": {
          "2024.01.09 08:30": {
              "open": 143.92400,
              "high": 143.98000,
              "low": 143.92000,
              "close": 143.92500,
              "tick_volume": 400.00000
          },
          "2024.01.09 08:35": {
              "open": 143.92400,
              "high": 143.97200,
              "low": 143.91600,
              "close": 143.92100,
              "tick_volume": 305.00000
          }
      }
  }
  mock_df = DataFrame.from_dict(
      data[f'{symbol}_{Config.timeframe}'], orient='index')

  # Assertions
  assert data == mock_data
  assert client.historic_data[symbol].equals(mock_df)


def test_is_historic_data_up_to_date_true():
  tz = pytz.timezone(str(Config.utc_timezone))
  Config.broker_timezone = tz
  df = DataFrame(
      index=['2024.01.20 01:05'],
      data={'open': [143.97200],
            'high': [144.01000],
            'low': [143.96800],
            'close': [143.99000],
            'tick_volume': [295]}
  )
  d = datetime(2024, 1, 20, 1, 5)
  with freeze_time(tz.localize(d)):
    assert MT_Client._is_historic_data_up_to_date(df)

  d = datetime(2024, 1, 20, 1, 8)
  with freeze_time(tz.localize(d)):
    assert MT_Client._is_historic_data_up_to_date(df)

  d = datetime(2024, 1, 20, 1, 10)
  with freeze_time(tz.localize(d)):
    assert not MT_Client._is_historic_data_up_to_date(df)


def test_check_historic_trades(tmp_path):

  # Copy the Bar_Data.json file to the temporary folder
  bar_data_path = tmp_path / 'Historic_Trades.json'
  original_bar_data_path = Path(f'{test_resources()}/Historic_Trades.json')
  shutil.copyfile(original_bar_data_path, bar_data_path)

  client = MT_Client()
  client.path_bar_data = bar_data_path

  # Call for the first time to read data
  client.check_bar_data()

  assert_data = {
      '2015257378': {
          'magic': 1696018543,
          'symbol': 'GBPCAD',
          'lots': 0.01,
          'type': 'sell',
          'entry': 'entry_out',
          'deal_time': '2023.09.29 23:52:28',
          'deal_price': 1.65396,
          'pnl': -2.45,
          'commission': -0.03,
          'swap': 0.00,
          'comment': '[sl 1.65410]'
      }
  }

  assert client.bar_data == assert_data

  # Does not change on second call
  client.check_bar_data()

  assert client.bar_data == assert_data

  # Write new data
  data = try_load_json(bar_data_path)
  data['2015257379'] = {
      'magic': 1696018343,
      'symbol': 'EURUSD',
      'lots': 0.01,
      'type': 'buy',
      'entry': 'entry_out',
      'deal_time': '2023.09.29 23:52:28',
      'deal_price': 1.65396,
      'pnl': -2.45,
      'commission': -0.03,
      'swap': 0.00,
      'comment': '[sl 1.65410]'
  }
  with open(bar_data_path, 'w') as f:
    f.write(json.dumps(data))

  # Now it does change
  client.check_bar_data()

  assert client.bar_data == data


def test_send_command(tmp_path):

  client = MT_Client()
  tmp_path = Path(tmp_path)
  client.path_commands_prefix = tmp_path / 'Commands_'

  # Acquire and release lock
  client.lock.acquire()
  assert client.lock.locked()

  client.lock.release()
  assert not client.lock.locked()

  # Rest of test
  client.send_command('TEST', 'test content')

  assert client.command_id == 1
  assert try_read_file('Commands_0.txt', tmp_path) == '<:1|TEST|test content:>'


def test_clean_all_command_files(tmp_path):

  client = MT_Client()
  client.path_commands_prefix = tmp_path

  # Create some files
  client.send_command('TEST', 'test content 1')
  client.send_command('TEST', 'test content 2')

  # Check they exist
  file1 = Path(f'{client.path_commands_prefix}0.txt')
  file2 = Path(f'{client.path_commands_prefix}1.txt')
  assert file1.exists() and file2.exists()

  # Clean them
  client.clean_all_command_files()

  # Check they are gone
  assert not file1.exists() and not file2.exists()


def test_clean_all_historic_files(tmp_path):

  client = MT_Client()
  client.path_historic_data = tmp_path

  # Create some files
  file1 = Path(join(tmp_path, 'Historic_Data_EURUSD.json'))
  file2 = Path(join(tmp_path, 'Historic_Data_USDJPY.json'))
  file1.touch()
  file2.touch()

  # Check they exist
  assert file1.exists() and file2.exists()

  # Clean them
  client.clean_all_historic_files()

  # Check they are gone
  assert not file1.exists() and not file2.exists()


def test_command_file_exist():
  client = MT_Client()
  client.path_commands_prefix = Path(f'{test_resources()}/Commands_')

  assert client.command_file_exist('GBPNZD')
  assert not client.command_file_exist('EURUSD')
