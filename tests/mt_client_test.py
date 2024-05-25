from pathlib import Path
from unittest.mock import patch
import shutil
from pandas import DataFrame
import json
from datetime import datetime, timedelta
import pytz
from freezegun import freeze_time
from os.path import join, exists

from tradeo.paths import resources_test_path
from tradeo.mt_client import MT_Client
from tradeo.config import Config
from tradeo.files import try_load_json, try_read_file
from tradeo.order import (
    Order,
    MutableOrderDetails,
    ImmutableOrderDetails,
    OrderPrice
)
from tradeo.mt_message import MT_MessageError, MT_MessageInfo
from tradeo.order_type import OrderType
from tradeo.event_handlers.basic_event_handler import BasicEventHandler


def test_set_agent_paths():
  mock_config = Config
  mock_config.mt_files_path = resources_test_path()

  with patch('tradeo.mt_client.Config', mock_config):
    mt_client = MT_Client()
    path_file = join(mock_config.mt_files_path, mt_client.prefix_files_path)

    # Method to test
    mt_client.set_agent_paths()

    assert mt_client.path_orders == Path(join(path_file, 'Orders.json'))
    assert mt_client.path_messages == Path(join(path_file, 'Messages.json'))
    assert mt_client.path_market_data == Path(
        join(path_file, 'Market_Data.json'))
    assert mt_client.path_bar_data == Path(join(path_file, 'Bar_Data.json'))
    assert mt_client.path_historical_data_prefix == Path(
        join(path_file, 'Historical_Data_'))
    assert mt_client.path_historical_trades == Path(join(
        path_file, 'Historical_Trades.json'))
    assert mt_client.path_orders_stored == Path(join(
        path_file, 'Orders_Stored.json'))
    assert mt_client.path_messages_stored == Path(join(
        path_file, 'Messages_Stored.json'))
    assert mt_client.path_commands_prefix == Path(join(path_file, 'Commands_'))


def test_invalid_file_path():
  mock_config = Config
  mock_config.mt_files_path = Path('invalid_path')
  with patch('tradeo.mt_client.Config', mock_config):
    mt_client = MT_Client()
    if hasattr(mt_client, 'path_orders'):
      delattr(mt_client, 'path_orders')
    mt_client.set_agent_paths()
    assert not hasattr(mt_client, 'path_orders')


def test_start_threads(tmp_path):
  mt_client = MT_Client(event_handler=BasicEventHandler())

  path = tmp_path / 'Orders.json'
  original_path = Path(f'{resources_test_path()}/AgentFiles/Orders.json')
  shutil.copyfile(original_path, path)
  mt_client.path_orders = path

  path = tmp_path / 'Messages.json'
  original_path = Path(f'{resources_test_path()}/AgentFiles/Messages.json')
  shutil.copyfile(original_path, path)
  mt_client.path_messages = path

  path = tmp_path / 'Market_Data.json'
  original_path = Path(f'{resources_test_path()}/AgentFiles/Market_Data.json')
  shutil.copyfile(original_path, path)
  mt_client.path_market_data = path

  path = tmp_path / 'Bar_Data.json'
  original_path = Path(f'{resources_test_path()}/AgentFiles/Bar_Data.json')
  shutil.copyfile(original_path, path)
  mt_client.path_bar_data = path

  path = tmp_path / 'Historical_Trades.json'
  original_path = Path(
      f'{resources_test_path()}/AgentFiles/Historical_Trades.json')
  shutil.copyfile(original_path, path)
  mt_client.path_historical_trades = path

  path = tmp_path / 'Orders_Stored.json'
  original_path = Path(
      f'{resources_test_path()}/AgentFiles/Orders_Stored.json')
  shutil.copyfile(original_path, path)
  mt_client.path_orders_stored = path

  path = tmp_path / 'Messages_Stored.json'
  original_path = Path(
      f'{resources_test_path()}/AgentFiles/Messages_Stored.json')
  shutil.copyfile(original_path, path)
  mt_client.path_messages_stored = path

  path = tmp_path / 'Commands_0.txt'
  original_path = Path(f'{resources_test_path()}/AgentFiles/Commands_0.txt')
  shutil.copyfile(original_path, path)
  mt_client.path_commands_prefix = path

  mt_client.start()
  mt_client.stop()
  mt_client.deactivate()


def test_check_messages(tmp_path):

  # Copy the Messages.json file to the temporary folder
  messages_path = tmp_path / 'Messages.json'
  original_messages_path = Path(
      f'{resources_test_path()}/AgentFiles/Messages.json')
  shutil.copyfile(original_messages_path, messages_path)

  mt_client = MT_Client()
  mt_client.path_messages = messages_path

  # Call for the first time to read messages
  mt_client.check_messages()

  assert_data = {
      'INFO': [MT_MessageInfo('2024.01.18 22:26:36', 'Dummy Info')],
      'ERROR': [
          MT_MessageError(
              '2024.01.18 22:26:36',
              'WRONG_FORMAT_START_IDENTIFIER',
              'Dummy Error'
          )
      ]
  }
  assert mt_client.get_info_messages() == assert_data['INFO']
  assert mt_client.get_error_messages() == assert_data['ERROR']

  # Does not change on second call
  mt_client.check_messages()

  assert mt_client.messages == assert_data

  # Now it does change
  info = MT_MessageInfo('2024.02.19 23:26:36', 'info description')
  error = MT_MessageError('2024.02.19 23:26:36',
                          'WRONG_FORMAT_START_IDENTIFIER', 'error description')

  mt_client.set_messages(info_messages=[info], error_messages=[error])
  mt_client.check_messages()

  assert_data['INFO'] = [info]
  assert_data['ERROR'] = [error]
  assert mt_client.messages == assert_data


def test_check_market_data(tmp_path):

  # Copy the Market_Data.json file to the temporary folder
  market_data_path = tmp_path / 'Market_Data.json'
  original_market_data_path = Path(
      f'{resources_test_path()}/AgentFiles/Market_Data.json')
  shutil.copyfile(original_market_data_path, market_data_path)

  mt_client = MT_Client()
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
  original_bar_data_path = Path(
      f'{resources_test_path()}/AgentFiles/Bar_Data.json')
  shutil.copyfile(original_bar_data_path, bar_data_path)

  mt_client = MT_Client()
  mt_client.path_bar_data = bar_data_path

  # Call for the first time to read data
  mt_client.check_bar_data()

  assert_data = {
      'EURUSD_M1': {
          'open': [1.08973, 1.08975],
          'high': [1.08979, 1.08981],
          'low': [1.08967, 1.08969],
          'close': [1.08975, 1.08977],
          'time': '2024-01-01T00:00:00.000Z',
          'tick_volume': 0.91761
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
      'close': [1.08995, 1.09000],
      'time': '2024-02-01T00:00:00.000Z',
      'tick_volume': 0.11111
  }
  with open(bar_data_path, 'w') as f:
    f.write(json.dumps(data))

  # Now it does change
  mt_client.check_bar_data()

  assert mt_client.bar_data == data


def test_check_open_orders(tmp_path):

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

  # Call for the first time to read orders
  mt_client.check_open_orders()

  assert_orders_data = [
      Order(
          MutableOrderDetails(
              prices=OrderPrice(
                  price=0.65754,
                  stop_loss=0.65443,
                  take_profit=0.00000
              ), lots=0.01
          ),
          ImmutableOrderDetails(
              symbol='AUDUSD',
              order_type=OrderType(buy=True, market=True),
              magic='1705617043',
              comment='this is a comment'
          ),
          ticket=2023993175
      ),
      Order(
          MutableOrderDetails(
              prices=OrderPrice(
                  price=0.65754,
                  stop_loss=0.65443,
                  take_profit=0.00000
              ), lots=0.01
          ),
          ImmutableOrderDetails(
              symbol='AUDUSD',
              order_type=OrderType(buy=False, market=False),
              magic='1705617043',
              comment='this is a comment'
          ),
          ticket=2023993176
      )
  ]
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
  data = {'orders': {}, 'account_info': {}}
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

  assert len(mt_client.open_orders) == 1
  assert mt_client.account_info == data['account_info']


def test_check_historical_data(tmp_path):

  symbol = 'USDJPY'
  prefix = 'AgentFiles'
  Path(tmp_path / prefix).mkdir()
  historical_path = tmp_path / f'{prefix}/Historical_Data_{symbol}.json'
  commands_path = tmp_path / f'{prefix}/Commands_0.txt'
  original_commands_path = Path(
      f'{resources_test_path()}/{prefix}/Commands_0.txt')
  shutil.copyfile(original_commands_path, commands_path)

  mt_client = MT_Client()
  mt_client.path_historical_data_prefix = Path(
      tmp_path / f'{prefix}/Historical_Data_'
  )
  mt_client.path_commands_prefix = tmp_path / f'{prefix}/Commands_'

  now_date = datetime.now(Config.broker_timezone)
  td = timedelta(minutes=now_date.minute % 5,
                 seconds=now_date.second,
                 microseconds=now_date.microsecond)
  rounded_now_date = now_date - td + timedelta(minutes=1)
  rounded_now_date_minus_5 = rounded_now_date - timedelta(minutes=5)
  data = {
      'USDJPY_M5': {
          f'{rounded_now_date_minus_5.strftime("%Y.%m.%d %H:%M")}': {
              'open': 143.92400,
              'high': 143.98000,
              'low': 143.92000,
              'close': 143.92500,
              'tick_volume': 400.00000
          },
          f'{rounded_now_date.strftime("%Y.%m.%d %H:%M")}': {
              'open': 143.92400,
              'high': 143.97200,
              'low': 143.91600,
              'close': 143.92100,
              'tick_volume': 305.00000
          }
      }
  }

  with open(historical_path, 'w') as f:
    f.write(json.dumps(data))

  # Assert successful symbols
  assert mt_client.successful_symbols == set()
  data = mt_client.check_historical_data(symbol)
  data_df = DataFrame.from_dict(
      data[f'{symbol}_{Config.timeframe}'], orient='index')
  assert data_df.shape[0] == 2
  assert mt_client.successful_symbols == {symbol}

  # Assert no remaining symbols
  mt_client._successful_symbols = set(Config.symbols)
  assert mt_client.check_historical_data(symbol) == {}


def test_is_historical_data_up_to_date_true():
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
  historical_trades_path = tmp_path / 'Historical_Trades.json'
  original_historical_trades_path = Path(
      f'{resources_test_path()}/AgentFiles/Historical_Trades.json')
  shutil.copyfile(original_historical_trades_path, historical_trades_path)

  mt_client = MT_Client()
  mt_client.path_historical_trades = historical_trades_path

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

  assert mt_client.historical_trades == assert_data

  # Does not change on second call
  mt_client.check_historical_trades()

  assert mt_client.historical_trades == assert_data

  # Write new data
  data = try_load_json(historical_trades_path)
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
  with open(historical_trades_path, 'w') as f:
    f.write(json.dumps(data))

  # Now it does change
  mt_client.check_historical_trades()

  assert mt_client.historical_trades == data


def test_send_command(tmp_path):

  tmp_path = Path(tmp_path)
  mt_client = MT_Client()
  mt_client.path_commands_prefix = tmp_path / 'Commands_'

  # Acquire and release lock
  mt_client.lock.acquire()
  assert mt_client.lock.locked()

  mt_client.lock.release()
  assert not mt_client.lock.locked()

  # Rest of test
  mt_client.send_command('TEST', 'test content')

  assert mt_client.command_id > 0
  assert '|TEST|test content:>' in try_read_file(
      tmp_path / 'Commands_0.txt')


def test_clean_all_command_files(tmp_path):
  mt_client = MT_Client()
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


def test_clean_all_historical_files(tmp_path):
  mt_client = MT_Client()
  mt_client.path_historical_data_prefix = Path(
      join(tmp_path, 'Historical_Data_'))

  # Create some files
  file1 = Path(join(tmp_path, 'Historical_Data_EURUSD.json'))
  file2 = Path(join(tmp_path, 'Historical_Data_USDJPY.json'))
  file1.touch()
  file2.touch()

  # Check they exist
  assert file1.exists()
  assert file2.exists()

  # Clean them
  mt_client.clean_all_historical_files()

  # Check they are gone
  assert not file1.exists()
  assert not file2.exists()


def test_command_file_exist():
  mt_client = MT_Client()
  mt_client.path_commands_prefix = Path(
      f'{resources_test_path()}/AgentFiles/Commands_')

  assert mt_client.command_file_exist('USDJPY')
  assert not mt_client.command_file_exist('EURUSD')


def test_clean_messages(tmp_path):
  mt_client = MT_Client()
  mt_client.path_messages = tmp_path
  m = {'INFO': ['test'], 'ERROR': ['error_test']}
  mt_client.messages = m  # type: ignore

  mt_client.clean_messages()
  assert mt_client.messages == {'INFO': [], 'ERROR': []}


def test_get_bid_ask(tmp_path):
  market_data_path = tmp_path / 'Market_Data.json'
  original_market_data_path = Path(
      f'{resources_test_path()}/AgentFiles/Market_Data.json')
  shutil.copyfile(original_market_data_path, market_data_path)
  mt_client = MT_Client()
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


def test_transform_json_orders_to_orders():
  mt_client = MT_Client()
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
          order_type=OrderType(buy=False, market=False),
          magic='1705617043',
          comment='this is a comment'
      ),
      ticket=2023993175
  )
  mt_client.open_orders = [order]
  json_orders = {
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
  orders = mt_client._transform_json_orders_to_orders(json_orders)
  assert len(orders) > 0
  assert orders[0] == order
  assert order.price == 0.65754
  assert order.stop_loss == 0.65443
  assert order.take_profit == 0.00000
  assert order.magic == '1705617043'
  assert order.comment == 'this is a comment'
  assert order.symbol == 'AUDUSD'
  assert order.lots == 0.01


@patch('tradeo.log.debug')
def test_place_break_even(mock_debug, tmp_path):
  mt_client = MT_Client()
  mt_client.path_commands_prefix = tmp_path / 'Commands_'
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
          order_type=OrderType(buy=True, market=True),
          magic='1705617043',
          comment='this is a comment'
      ),
      ticket=2023993175
  )
  mt_client.place_break_even(order)
  mock_debug.assert_called_with(f'Break even placed in {order.magic}')


@patch('tradeo.files.get_default_path')
def test_create_new_order(mock_default_path, tmp_path):
  # Make data_path() return the temporary directory
  mock_default_path.return_value = tmp_path

  # Market Data
  market_data_path = tmp_path / 'Market_Data.json'
  original_market_data_path = Path(
      f'{resources_test_path()}/AgentFiles/Market_Data.json')
  shutil.copyfile(original_market_data_path, market_data_path)
  mt_client = MT_Client()
  mt_client.path_market_data = market_data_path
  mt_client.check_market_data()

  # Command files
  mt_client.path_commands_prefix = tmp_path / 'Commands_'

  order = Order(
      MutableOrderDetails(
          prices=OrderPrice(
              price=0.65754,
              stop_loss=0.65443,
              take_profit=0.00000
          ), lots=0.01
      ),
      ImmutableOrderDetails(
          symbol='EURUSD',
          order_type=OrderType(buy=True, market=False),
          magic='1705617043',
          comment='this is a comment'
      ),
      ticket=2023993175
  )
  mt_client.create_new_order(order)
  file_path = f'{mt_client.path_commands_prefix}{0}.txt'
  assert exists(file_path)


def test_get_remaining_symbols():
  mt_client = MT_Client()
  mt_client._successful_symbols = {'EURUSD', 'USDCAD'}
  result = mt_client.get_remaining_symbols()
  assert len(result) == len(Config.symbols) - 2
  assert 'EURUSD' not in result


def test_get_balance(tmp_path):
  # Copy the Orders.json file to the temporary folder
  orders_path = tmp_path / 'Orders.json'
  original_orders_path = Path(
      f'{resources_test_path()}/AgentFiles/Orders.json')
  shutil.copyfile(original_orders_path, orders_path)

  # Copy the Orders_Stored.json file to the temporary folder
  orders_stored_path = tmp_path / 'Orders_Stored.json'
  original_path = Path(
      f'{resources_test_path()}/AgentFiles/Orders_Stored.json')
  shutil.copyfile(original_path, orders_stored_path)

  mt_client = MT_Client()
  mt_client.path_orders = orders_path
  mt_client.path_orders_stored = orders_stored_path

  # Call for the first time to read orders
  mt_client.check_open_orders()

  assert mt_client.get_balance() > 0

  # No account info
  with open(orders_path, 'w') as f:
    f.write(json.dumps({
        'account_info': {}, 'orders': {}
    }))
  assert mt_client.get_balance() == -1.0


def test_subscribe_symbols(tmp_path):
  mt_client = MT_Client()
  mt_client.path_commands_prefix = tmp_path / 'Commands_'
  mt_client.subscribe_symbols(Config.symbols)
  file_path = f'{mt_client.path_commands_prefix}{0}.txt'
  assert exists(file_path)


def test_subscribe_symbols_bar_data(tmp_path):
  mt_client = MT_Client()
  mt_client.path_commands_prefix = tmp_path / 'Commands_'
  mt_client.subscribe_symbols_bar_data([['EURUSD', 'M1'], ['GBPUSD', 'H1']])
  file_path = f'{mt_client.path_commands_prefix}{0}.txt'
  assert exists(file_path)


def test_get_historical_data(tmp_path):
  mt_client = MT_Client()
  mt_client.path_commands_prefix = tmp_path / 'Commands_'
  mt_client.get_historical_data(
      'USDJPY',
      '5M',
  )
  file_path = f'{mt_client.path_commands_prefix}{0}.txt'
  assert exists(file_path)


def test_get_historical_trades(tmp_path):
  mt_client = MT_Client()
  mt_client.path_commands_prefix = tmp_path / 'Commands_'
  mt_client.get_historical_trades()
  file_path = f'{mt_client.path_commands_prefix}{0}.txt'
  assert exists(file_path)


def test_modify_pending_order():
  mt_client = MT_Client()
  order = Order(
      MutableOrderDetails(
          prices=OrderPrice(
              price=0.1111111,
              stop_loss=0.65443,
              take_profit=0.00000
          ), lots=0.01
      ),
      ImmutableOrderDetails(
          symbol='AUDUSD',
          order_type=OrderType(buy=True, market=False),
          magic='1705617043',
          comment='this is a comment'
      ),
      ticket=2023993175
  )
  bid, ask = 0.1, 0.1
  mt_client._modify_pending_order(order, bid, ask)
  bid, ask = 0.1, 0.2
  mt_client._modify_pending_order(order, bid, ask)
  order = Order(
      MutableOrderDetails(
          prices=OrderPrice(
              price=0.1111111,
              stop_loss=0.65443,
              take_profit=0.00000
          ), lots=0.01
      ),
      ImmutableOrderDetails(
          symbol='AUDUSD',
          order_type=OrderType(buy=False, market=False),
          magic='1705617043',
          comment='this is a comment'
      ),
      ticket=2023993176
  )
  bid, ask = 0.1, 0.1
  mt_client._modify_pending_order(order, bid, ask)
  bid, ask = 0.2, 0.1
  mt_client._modify_pending_order(order, bid, ask)
  assert True


def test_send_close_order_command(tmp_path):
  mt_client = MT_Client()
  mt_client.path_commands_prefix = tmp_path / 'Commands_'
  mt_client.send_close_order_command(ticket=2023993175)
  file_path = f'{mt_client.path_commands_prefix}{0}.txt'
  assert exists(file_path)


def test_send_close_all_orders_command(tmp_path):
  mt_client = MT_Client()
  mt_client.path_commands_prefix = tmp_path / 'Commands_'
  mt_client.send_close_all_orders_command()
  file_path = f'{mt_client.path_commands_prefix}{0}.txt'
  assert exists(file_path)


def test_send_close_orders_by_symbol_command(tmp_path):
  mt_client = MT_Client()
  mt_client.path_commands_prefix = tmp_path / 'Commands_'
  mt_client.send_close_orders_by_symbol_command('USDJPY')
  file_path = f'{mt_client.path_commands_prefix}{0}.txt'
  assert exists(file_path)


@patch('tradeo.mt_client.MT_Client.get_balance')
@patch('tradeo.mt_client.MT_Client.get_bid_ask')
def test_get_lot_size(bid_ask_mock, balance_mock):
  bid_ask_mock.return_value = (1.08452, 1.08452)
  balance_mock.return_value = 1000
  mt_client = MT_Client()
  order = Order(
      MutableOrderDetails(
          prices=OrderPrice(
              price=1.08452,
              stop_loss=1.08033,
              take_profit=1.09040
          )
      ),
      ImmutableOrderDetails(
          symbol='EURUSD',
          order_type=OrderType(buy=True, market=True),
          magic='1705617043',
          comment='this is a comment'
      ),
      ticket=2023993175
  )
  lots = mt_client.get_lot_size(order=order, risk_ratio=1)
  assert lots == 0.03
