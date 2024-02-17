from pathlib import Path
from unittest.mock import patch, MagicMock
from tradingbot.forex_client import MT_Client, mt_client
from tradingbot.config import Config
import shutil
from pandas import DataFrame
from tradingbot.files import try_load_json, try_read_file
import json
from datetime import datetime
import pytz
from freezegun import freeze_time
from tradingbot.paths import resources_test_path
from os.path import join
from tradingbot.order import (
    Order,
    MutableOrderDetails,
    ImmutableOrderDetails,
    OrderPrice
)
from tradingbot.order_type import OrderType


def test_set_agent_paths():
  mock_config = MagicMock()
  mock_config.mt_files_path = resources_test_path()

  with patch('tradingbot.forex_client.Config', mock_config):
    path_file = join(mock_config.mt_files_path, mt_client.prefix_files_path)

    # Method to test
    mt_client.set_agent_paths()

    assert mt_client.path_orders == Path(join(path_file, 'Orders.json'))
    assert mt_client.path_messages == Path(join(path_file, 'Messages.json'))
    assert mt_client.path_market_data == Path(
        join(path_file, 'Market_Data.json'))
    assert mt_client.path_bar_data == Path(join(path_file, 'Bar_Data.json'))
    assert mt_client.path_historic_data == Path(join(path_file))
    assert mt_client.path_historic_trades == Path(join(
        path_file, 'Historic_Trades.json'))
    assert mt_client.path_orders_stored == Path(join(
        path_file, 'Orders_Stored.json'))
    assert mt_client.path_messages_stored == Path(join(
        path_file, 'Messages_Stored.json'))
    assert mt_client.path_commands_prefix == Path(join(path_file, 'Commands_'))


def test_check_messages(tmp_path):

  # Copy the Messages.json file to the temporary folder
  messages_path = tmp_path / 'Messages.json'
  original_messages_path = Path(f'{resources_test_path()}/Messages.json')
  shutil.copyfile(original_messages_path, messages_path)

  mt_client.path_messages = messages_path

  # Call for the first time to read messages
  mt_client.check_messages()

  assert_data = {
      'INFO': [['2024.01.18 22:26:36', 'Dummy Info']],
      'ERROR': [['2024.01.18 22:26:36', 'Dummy Error']]
  }
  assert mt_client.messages == assert_data

  # Does not change on second call
  mt_client.check_messages()

  assert mt_client.messages == assert_data

  # Write new message
  data = try_load_json(messages_path)
  data['33333333'] = {
      'type': 'INFO', 'time': '2024.01.18 22:26:36', 'message': 'New Message'
  }
  with open(messages_path, 'w') as f:
    f.write(json.dumps(data))

  # Now it does change
  mt_client.check_messages()

  assert_data['INFO'].append(['2024.01.18 22:26:36', 'New Message'])
  assert mt_client.messages == assert_data


def test_check_market_data(tmp_path):

  # Copy the Market_Data.json file to the temporary folder
  market_data_path = tmp_path / 'Market_Data.json'
  original_market_data_path = Path(f'{resources_test_path()}/Market_Data.json')
  shutil.copyfile(original_market_data_path, market_data_path)

  mt_client.path_market_data = market_data_path

  # Call for the first time to read data
  mt_client.check_market_data()

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
  assert mt_client.market_data == assert_data

  # Does not change on second call
  mt_client.check_market_data()

  assert mt_client.market_data == assert_data

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
  mt_client.check_market_data()

  assert mt_client.market_data == data


def test_check_bar_data(tmp_path):

  # Copy the Bar_Data.json file to the temporary folder
  bar_data_path = tmp_path / 'Bar_Data.json'
  original_bar_data_path = Path(f'{resources_test_path()}/Bar_Data.json')
  shutil.copyfile(original_bar_data_path, bar_data_path)

  mt_client.path_bar_data = bar_data_path

  # Call for the first time to read data
  mt_client.check_bar_data()

  assert_data = {
      'EURUSD_M1': {
          'open': [1.08973, 1.08975],
          'high': [1.08979, 1.08981],
          'low': [1.08967, 1.08969],
          'close': [1.08975, 1.08977]
      }
  }

  assert mt_client.bar_data == assert_data

  # Does not change on second call
  mt_client.check_bar_data()

  assert mt_client.bar_data == assert_data

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
  mt_client.check_bar_data()

  assert mt_client.bar_data == data


def test_check_open_orders(tmp_path):

  # Copy the Orders.json file to the temporary folder
  orders_path = tmp_path / 'Orders.json'
  original_orders_path = Path(f'{resources_test_path()}/Orders.json')
  shutil.copyfile(original_orders_path, orders_path)

  # Copy the Orders_Stored.json file to the temporary folder
  orders_stored_path = tmp_path / 'Orders_Stored.json'
  original_orders_stored_path = Path(
      f'{resources_test_path()}/Orders_Stored.json')
  shutil.copyfile(original_orders_stored_path, orders_stored_path)

  mt_client.path_orders = orders_path
  mt_client.path_orders_stored = orders_stored_path

  # Call for the first time to read orders
  mt_client.check_open_orders()

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
          'comment': 'this is a comment'
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
  assert mt_client.open_orders == assert_orders_data
  assert mt_client.account_info == assert_account_data

  # Does not change on second call
  mt_client.check_open_orders()

  assert mt_client.open_orders == assert_orders_data
  assert mt_client.account_info == assert_account_data

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
  mt_client.check_open_orders()

  assert mt_client.open_orders == data['orders']
  assert mt_client.account_info == data['account_info']


def test_check_historical_data(tmp_path):

  symbol = 'USDJPY'

  mt_client.path_historic_data = tmp_path
  mt_client.path_historic_data = resources_test_path()

  data = mt_client.check_historical_data(symbol)
  mock_data = {
      'USDJPY_M5': {
          '2024.01.09 08:30': {
              'open': 143.92400,
              'high': 143.98000,
              'low': 143.92000,
              'close': 143.92500,
              'tick_volume': 400.00000
          },
          '2024.01.09 08:35': {
              'open': 143.92400,
              'high': 143.97200,
              'low': 143.91600,
              'close': 143.92100,
              'tick_volume': 305.00000
          }
      }
  }
  mock_df = DataFrame.from_dict(
      data[f'{symbol}_{Config.timeframe}'], orient='index')

  # Assertions
  assert data == mock_data
  assert mt_client.historic_data[symbol].equals(mock_df)


def test_is_historic_data_up_to_date_true():
  tz = pytz.timezone(str(Config.utc_timezone))
  Config.broker_timezone = tz
  df = DataFrame(
      index=['2024.01.20 01:05'],
      data={
          'open': [143.97200],
          'high': [144.01000],
          'low': [143.96800],
          'close': [143.99000],
          'tick_volume': [295]
      }
  )
  d = datetime(2024, 1, 20, 1, 5)
  with freeze_time(tz.localize(d)):
    assert MT_Client._is_historical_data_up_to_date(df)

  d = datetime(2024, 1, 20, 1, 8)
  with freeze_time(tz.localize(d)):
    assert MT_Client._is_historical_data_up_to_date(df)

  d = datetime(2024, 1, 20, 1, 10)
  with freeze_time(tz.localize(d)):
    assert not MT_Client._is_historical_data_up_to_date(df)


def test_check_historical_trades(tmp_path):

  # Copy the Bar_Data.json file to the temporary folder
  historic_trades_path = tmp_path / 'Historic_Trades.json'
  original_historic_trades_path = Path(
      f'{resources_test_path()}/Historic_Trades.json')
  shutil.copyfile(original_historic_trades_path, historic_trades_path)

  mt_client.path_historic_trades = historic_trades_path

  # Call for the first time to read data
  mt_client.check_historical_trades()

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

  assert mt_client.historic_trades == assert_data

  # Does not change on second call
  mt_client.check_historical_trades()

  assert mt_client.historic_trades == assert_data

  # Write new data
  data = try_load_json(historic_trades_path)
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
  with open(historic_trades_path, 'w') as f:
    f.write(json.dumps(data))

  # Now it does change
  mt_client.check_historical_trades()

  assert mt_client.historic_trades == data


def test_send_command(tmp_path):

  tmp_path = Path(tmp_path)
  mt_client.path_commands_prefix = tmp_path / 'Commands_'

  # Acquire and release lock
  mt_client.lock.acquire()
  assert mt_client.lock.locked()

  mt_client.lock.release()
  assert not mt_client.lock.locked()

  # Rest of test
  mt_client.send_command('TEST', 'test content')

  assert mt_client.command_id == 1
  assert try_read_file('Commands_0.txt', tmp_path) == '<:1|TEST|test content:>'


def test_clean_all_command_files(tmp_path):

  mt_client.path_commands_prefix = tmp_path

  # Create some files
  mt_client.send_command('TEST', 'test content 1')
  mt_client.send_command('TEST', 'test content 2')

  # Check they exist
  file1 = Path(f'{mt_client.path_commands_prefix}0.txt')
  file2 = Path(f'{mt_client.path_commands_prefix}1.txt')
  assert file1.exists()
  assert file2.exists()

  # Clean them
  mt_client.clean_all_command_files()

  # Check they are gone
  assert not file1.exists()
  assert not file2.exists()


def test_clean_all_historic_files(tmp_path):

  mt_client.path_historic_data = tmp_path

  # Create some files
  file1 = Path(join(tmp_path, 'Historic_Data_EURUSD.json'))
  file2 = Path(join(tmp_path, 'Historic_Data_USDJPY.json'))
  file1.touch()
  file2.touch()

  # Check they exist
  assert file1.exists()
  assert file2.exists()

  # Clean them
  mt_client.clean_all_historic_files()

  # Check they are gone
  assert not file1.exists()
  assert not file2.exists()


def test_command_file_exist():
  mt_client.path_commands_prefix = Path(f'{resources_test_path()}/Commands_')

  assert mt_client.command_file_exist('GBPNZD')
  assert not mt_client.command_file_exist('EURUSD')


def test_clean_messages():
  m = {'INFO': ['test'], 'ERROR': ['error_test']}
  mt_client.messages = m  # type: ignore
  mt_client.clean_messages()
  assert mt_client.messages == {'INFO': [], 'ERROR': []}


def test_get_bid_ask(tmp_path):
  market_data_path = tmp_path / 'Market_Data.json'
  original_market_data_path = Path(f'{resources_test_path()}/Market_Data.json')
  shutil.copyfile(original_market_data_path, market_data_path)
  mt_client.path_market_data = market_data_path
  mt_client.check_market_data()

  bid, ask = mt_client.get_bid_ask('EURUSD')
  assert isinstance(bid, float)
  assert isinstance(ask, float)
  assert bid != 0
  assert ask != 0

  bid, ask = mt_client.get_bid_ask('DUMMY_SYMBOL')
  assert bid == 0
  assert ask == 0


def test_get_open_orders():
  mt_client.open_orders = {
      '2023993175': {
          'magic': 1705617043,
          'symbol': 'AUDUSD',
          'lots': 0.01,
          'type': 'buy',
          'open_price': 0.65754,
          'open_time': '2024.01.19 00:30:43',
          'SL': 0.65443,
          'TP': 0.00000,
          'pnl': -0.59,
          'swap': 0.00,
          'comment': 'this is a comment'
      }
  }
  order = Order(
      MutableOrderDetails(
          prices=OrderPrice(
              price=0.65754,
              stop_loss=0.65443,
              take_profit=0.00000
          ), lots=0.01
      ),
      ImmutableOrderDetails(
          symbol='AUDUSD',
          order_type=OrderType.BUY,
          magic='1705617043',
          comment='this is a comment'
      ),
      ticket=2023993175
  )
  orders = mt_client.get_open_orders()
  assert len(orders) == 1
  assert orders[0] == order
  assert order.price == 0.65754
  assert order.stop_loss == 0.65443
  assert order.take_profit == 0.00000
  assert order.magic == '1705617043'
  assert order.comment == 'this is a comment'
  assert order.symbol == 'AUDUSD'
  assert order.lots == 0.01


@patch('tradingbot.log.log.debug')
def test_place_break_even(mock_debug, tmp_path):
  mt_client.path_commands_prefix = tmp_path
  order = Order(
      MutableOrderDetails(
          prices=OrderPrice(
              price=0.65754,
              stop_loss=0.65443,
              take_profit=0.00000
          ), lots=0.01
      ),
      ImmutableOrderDetails(
          symbol='AUDUSD',
          order_type=OrderType.BUY,
          magic='1705617043',
          comment='this is a comment'
      ),
      ticket=2023993175
  )
  mt_client.place_break_even(order)
  mock_debug.assert_called_with(f'Break even placed in {order.magic}')


def test_get_pip():
  assert mt_client.get_pip('GBPUSD') == 0.0001
  assert mt_client.get_pip('USDJPY') == 0.01
