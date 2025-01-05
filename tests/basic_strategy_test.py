from pandas import DataFrame
import numpy as np
from datetime import datetime
from unittest.mock import patch
from pathlib import Path
from freezegun import freeze_time
import pytz
import shutil

from tradeo.log import log
from tradeo.order_type import OrderType
from tradeo.config import Config
from tradeo.paths import resources_test_path
from tradeo.mt_client import MT_Client
from tradeo.ohlc import OHLC
from tradeo.strategies.basic_strategy import BasicStrategy
from tradeo.order import (
    Order,
    MutableOrderDetails,
    ImmutableOrderDetails,
    OrderPrice
)


def test_indicator():
  highs = np.array([1, 2, 3, 4, 5, 6, 50, 1, 2, 3, 4, 5, 6, 100, 1, 2, 3])
  opens = highs
  lows = np.array(
      [11, 12, 13, 14, 15, 16, 1, 11, 12, 13, 14, 15, 16, 5, 11, 12, 13])
  closes = lows

  data = OHLC(DataFrame({
      'open': opens,
      'high': highs,
      'low': lows,
      'close': closes
  }))
  mt_client = MT_Client()
  strategy = BasicStrategy(mt_client)
  assert isinstance(strategy.indicator(data, 'EURUSD', datetime.now()), Order)


def test_check_order_viability():
  mt_client = MT_Client()
  strategy = BasicStrategy(mt_client)
  order = Order(
      MutableOrderDetails(
          prices=OrderPrice(
              price=2,
              stop_loss=1,
              take_profit=4
          ), lots=0.01
      ),
      ImmutableOrderDetails(
          symbol='EURUSD',
          order_type=OrderType(buy=True, market=True),
          magic='123456789',
          comment=''
      )
  )

  # Viable profit risk
  tz = pytz.timezone(str(Config.utc_timezone))
  d = datetime(2024, 1, 9, 12, 5)
  with freeze_time(tz.localize(d)):
    assert strategy.check_order_viability(order, min_risk_profit=1.5)

  # Not viable profit risk
  with freeze_time(tz.localize(d)):
    assert not strategy.check_order_viability(order, min_risk_profit=3)


@patch.object(log, 'debug')
def test_handle_pending_orders(mock_debug, tmp_path):
  mt_client = MT_Client()
  strategy = BasicStrategy(mt_client)
  mt_client.path_commands_prefix = tmp_path

  order = Order(
      MutableOrderDetails(
          prices=OrderPrice(
              price=2,
              stop_loss=1,
              take_profit=4
          ), lots=0.01
      ),
      ImmutableOrderDetails(
          symbol='EURUSD',
          order_type=OrderType(buy=True, market=True),
          magic='1999999999',
          comment=''
      )
  )
  time_threshold = 60

  tz = pytz.timezone(str(Config.broker_timezone))
  d = datetime(2024, 1, 1, 0, 0)
  with freeze_time(tz.localize(d)):
    strategy.handle_pending_orders(order, time_threshold)
    mock_debug.assert_called_with(
        f'Close order {order.magic} due to time threshold')


@patch.object(log, 'debug')
def test_handle_filled_orders(mock_debug, tmp_path):
  mt_client = MT_Client()
  strategy = BasicStrategy(mt_client)
  mt_client.path_commands_prefix = tmp_path

  order = Order(
      MutableOrderDetails(
          prices=OrderPrice(
              price=2,
              stop_loss=1,
              take_profit=4
          ), lots=0.01
      ),
      ImmutableOrderDetails(
          symbol='EURUSD',
          order_type=OrderType(buy=True, market=True),
          magic='1999999999',
          comment=''
      )
  )
  time_threshold = 60

  tz = pytz.timezone(str(Config.broker_timezone))
  d = datetime(2024, 1, 1, 0, 0)
  with freeze_time(tz.localize(d)):
    strategy.handle_filled_orders(order, time_threshold, 0)
    mock_debug.assert_called_with(
        f'Close order {order.magic} due to time threshold')


def test_check_if_break_even_can_be_placed(tmp_path):

  # Prepare the test to obtain bid and ask
  market_data_path = tmp_path / 'Market_Data.json'
  original_market_data_path = Path(
      f'{resources_test_path()}/AgentFiles/Market_Data.json')
  shutil.copyfile(original_market_data_path, market_data_path)
  mt_client = MT_Client()
  mt_client.path_market_data = market_data_path
  mt_client.path_commands_prefix = tmp_path
  mt_client.check_market_data()

  order = Order(
      MutableOrderDetails(
          prices=OrderPrice(
              price=2,
              stop_loss=1,
              take_profit=4
          ), lots=0.01
      ),
      ImmutableOrderDetails(
          symbol='EURUSD',
          order_type=OrderType(buy=True, market=True),
          magic='1999999999',
          comment=''
      )
  )
  open_time = datetime.fromtimestamp(
      int(order.magic)).astimezone(Config.utc_timezone)
  current_datetime = datetime.now(Config.utc_timezone)
  break_even_time_threshold = 60
  break_even_per_threshold = 0

  strategy = BasicStrategy(mt_client)
  assert strategy._check_if_break_even_can_be_placed(
      order,
      open_time,
      current_datetime,
      break_even_time_threshold,
      break_even_per_threshold
  )
