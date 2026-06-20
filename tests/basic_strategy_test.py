from pandas import DataFrame
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch
from freezegun import freeze_time
import pytz

from tradeo.log import log
from tradeo.order_type import OrderType
from tradeo.config import Config
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
  order._immutable_details.magic = str(
      round((tz.localize(d) - timedelta(seconds=120)).timestamp())
  )
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
  order._immutable_details.magic = str(
      round((tz.localize(d) - timedelta(seconds=120)).timestamp())
  )
  with freeze_time(tz.localize(d)):
    strategy.handle_filled_orders(order, time_threshold, 0)
    mock_debug.assert_called_with(
        f'Close order {order.magic} due to time threshold')


def test_check_if_break_even_can_be_placed():
  mt_client = _BreakEvenMTClient(bid=1.2500, ask=1.2502)
  order = Order(
      MutableOrderDetails(
          prices=OrderPrice(
              price=1.2,
              stop_loss=1,
              take_profit=1.4
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


class _BreakEvenMTClient:
  def __init__(self, bid, ask):
    self.bid = bid
    self.ask = ask
    self.closed_tickets = []
    self.break_even_orders = []

  def get_bid_ask(self, symbol):
    _ = symbol
    return self.bid, self.ask

  def send_close_order_command(self, ticket):
    self.closed_tickets.append(ticket)

  def place_break_even(self, order, log_comment=''):
    self.break_even_orders.append((order.ticket, log_comment))


@patch.object(log, 'debug')
def test_check_if_break_even_skips_buy_when_stop_is_already_crossed(
    mock_debug
):
  _ = mock_debug
  mt_client = _BreakEvenMTClient(bid=1.199, ask=1.1992)
  strategy = BasicStrategy(mt_client)
  order = _break_even_order(buy=True)

  result = strategy._check_if_break_even_can_be_placed(
      order,
      datetime.now(Config.utc_timezone),
      datetime.now(Config.utc_timezone),
      break_even_time_threshold=0,
      break_even_per_threshold=1,
  )

  assert not result
  assert mt_client.closed_tickets == []
  assert mt_client.break_even_orders == []


@patch.object(log, 'debug')
def test_check_if_break_even_skips_sell_when_stop_is_already_crossed(
    mock_debug
):
  _ = mock_debug
  mt_client = _BreakEvenMTClient(bid=1.2008, ask=1.2009)
  strategy = BasicStrategy(mt_client)
  order = _break_even_order(buy=False)

  result = strategy._check_if_break_even_can_be_placed(
      order,
      datetime.now(Config.utc_timezone),
      datetime.now(Config.utc_timezone),
      break_even_time_threshold=0,
      break_even_per_threshold=1,
  )

  assert not result
  assert mt_client.closed_tickets == []
  assert mt_client.break_even_orders == []


def test_check_if_break_even_places_stop_when_not_crossed():
  mt_client = _BreakEvenMTClient(bid=1.2500, ask=1.2502)
  strategy = BasicStrategy(mt_client)
  order = _break_even_order(buy=True)

  result = strategy._check_if_break_even_can_be_placed(
      order,
      datetime.now(Config.utc_timezone),
      datetime.now(Config.utc_timezone),
      break_even_time_threshold=0,
      break_even_per_threshold=1,
  )

  assert result
  assert mt_client.closed_tickets == []
  assert mt_client.break_even_orders == [
      (order.ticket, 'Time threshold reached')
  ]


def test_check_if_break_even_waits_for_profit_after_time_threshold():
  mt_client = _BreakEvenMTClient(bid=1.1900, ask=1.1902)
  strategy = BasicStrategy(mt_client)
  order = _break_even_order(buy=True)

  result = strategy._check_if_break_even_can_be_placed(
      order,
      datetime.now(Config.utc_timezone),
      datetime.now(Config.utc_timezone),
      break_even_time_threshold=0,
      break_even_per_threshold=1,
  )

  assert not result
  assert mt_client.closed_tickets == []
  assert mt_client.break_even_orders == []


def test_check_if_break_even_waits_for_profit_after_percentage_threshold():
  mt_client = _BreakEvenMTClient(bid=1.1900, ask=1.1902)
  strategy = BasicStrategy(mt_client)
  order = _break_even_order(buy=True)

  result = strategy._check_if_break_even_can_be_placed(
      order,
      datetime.now(Config.utc_timezone),
      datetime.now(Config.utc_timezone),
      break_even_time_threshold=3600,
      break_even_per_threshold=-1,
  )

  assert not result
  assert mt_client.closed_tickets == []
  assert mt_client.break_even_orders == []


def test_check_if_break_even_uses_sell_profit_direction_for_percentage():
  mt_client = _BreakEvenMTClient(bid=1.0988, ask=1.0990)
  strategy = BasicStrategy(mt_client)
  order = _break_even_order(buy=False)

  result = strategy._check_if_break_even_can_be_placed(
      order,
      datetime.now(Config.utc_timezone),
      datetime.now(Config.utc_timezone),
      break_even_time_threshold=3600,
      break_even_per_threshold=0.5,
  )

  assert result
  assert mt_client.closed_tickets == []
  assert mt_client.break_even_orders == [
      (order.ticket, 'Price percentage reached')
  ]


def _break_even_order(buy=True):
  return Order(
      MutableOrderDetails(
          prices=OrderPrice(
              price=1.2,
              stop_loss=1.0 if buy else 1.4,
              take_profit=1.4 if buy else 1.0,
          ), lots=0.01
      ),
      ImmutableOrderDetails(
          symbol='EURUSD',
          order_type=OrderType(buy=buy, market=True),
          magic='1999999999',
          comment=''
      ),
      ticket=123,
  )
