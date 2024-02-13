from unittest.mock import patch
from tradingbot.strategies.strategy import Strategy
from tradingbot.order import (
    Order,
    MutableOrderDetails,
    ImmutableOrderDetails,
    OrderPrice
)
import shutil
from tradingbot.order_type import OrderType
from tradingbot.forex_client import mt_client
from datetime import datetime
from tradingbot.config import Config
from tradingbot.paths import resources_test_path
from pathlib import Path


def test_check_order_viability():
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
          order_type=OrderType.BUY,
          magic='123456789',
          comment=''
      )
  )

  # Viable profit risk
  assert Strategy.check_order_viability(order, min_risk_profit=1.5)

  # Not viable profit risk
  assert not Strategy.check_order_viability(order, min_risk_profit=3)


@patch('tradingbot.log.log.debug')
def test_handle_limit_orders(mock_debug, tmp_path):

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
          order_type=OrderType.BUY,
          magic='9999999999',
          comment=''
      )
  )
  time_threshold = 60

  Strategy.handle_limit_orders(order, time_threshold)

  mock_debug.assert_called_with(
      f'Close order {order.magic} due to time threshold')


@patch('tradingbot.log.log.debug')
def test_handle_filled_orders(mock_debug, tmp_path):
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
          order_type=OrderType.BUY,
          magic='9999999999',
          comment=''
      )
  )
  time_threshold = 60

  Strategy.handle_filled_orders(order, time_threshold, 0)

  mock_debug.assert_called_with(
      f'Close order {order.magic} due to time threshold')


def test_check_if_break_even_can_be_placed(tmp_path):

  # Prepare the test to obtain bid and ask
  market_data_path = tmp_path / 'Market_Data.json'
  original_market_data_path = Path(f'{resources_test_path()}/Market_Data.json')
  shutil.copyfile(original_market_data_path, market_data_path)
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
          order_type=OrderType.BUY,
          magic='9999999999',
          comment=''
      )
  )
  open_time = datetime.fromtimestamp(
      int(order.magic)).astimezone(Config.utc_timezone)
  current_datetime = datetime.now(Config.utc_timezone)
  break_even_time_threshold = 60
  break_even_per_threshold = 0

  assert Strategy._check_if_break_even_can_be_placed(
      order,
      open_time,
      current_datetime,
      break_even_time_threshold,
      break_even_per_threshold
  )