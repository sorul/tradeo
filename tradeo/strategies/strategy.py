"""Abstract class for strategies."""
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Union, TYPE_CHECKING

from tradeo.config import Config
from tradeo.log import log
if TYPE_CHECKING:
  from tradeo.order import Order
  from tradeo.ohlc import OHLC
  from tradeo.mt_client import MT_Client


class Strategy(ABC):
  """This class should not be instantiated."""

  def __init__(self, strategy_name: str):
    """Initialize the attributes."""
    self.strategy_name = strategy_name

  @abstractmethod
  def indicator(
          self,
          ohlc: OHLC,
          symbol: str,
          date: datetime
  ) -> Union[Order, None]:
    """Return an order if the strategy is triggered."""

  @staticmethod
  def check_order_viability(
          mt_client: MT_Client,
          order: Order,
          min_risk_profit: float = 1.5,
          **kwargs
  ) -> bool:
    """Check if the order is viable."""
    _ = kwargs
    symbol = order.symbol
    orders = [o for o in mt_client.open_orders if o.symbol == symbol]
    c1 = len(orders) == 0
    c2 = order.risk_benefit() > min_risk_profit
    # High spread
    c3 = datetime.now(Config.utc_timezone).hour not in [22, 23, 0]
    return c1 and c2 and c3

  @staticmethod
  def handle_pending_orders(
          mt_client: MT_Client,
          order: Order,
          time_threshold: int = 3600
  ) -> None:
    """Handle limit orders based on the time threshold."""
    try:
      open_time = datetime.fromtimestamp(
          int(order.magic)).astimezone(Config.utc_timezone)
      current_datetime = datetime.now(Config.utc_timezone)
      if (current_datetime - open_time).seconds > time_threshold:
        mt_client.send_close_orders_by_magic_command(order.magic)
        log.debug(f'Close order {order.magic} due to time threshold')
    except ValueError:  # int(order.magic)
      pass

  @staticmethod
  def handle_filled_orders(
      mt_client: MT_Client,
      order: Order,
      time_threshold: int = 3600 * 24,
      break_even_time_threshold: int = 3600 * 12,
      break_even_per_threshold: float = 0.75,
      **kwargs
  ) -> None:
    """Handle filled orders by closing them or placing a break even."""
    _ = kwargs
    try:
      open_time = datetime.fromtimestamp(
          int(order.magic)).astimezone(Config.utc_timezone)
      current_datetime = datetime.now(Config.utc_timezone)

      # Check if the order can be closed based on the time threshold
      if (current_datetime - open_time).seconds > time_threshold:
        mt_client.send_close_orders_by_magic_command(order.magic)
        log.debug(f'Close order {order.magic} due to time threshold')

      # Check if a break even can be placed
      else:
        Strategy._check_if_break_even_can_be_placed(
            mt_client,
            order,
            open_time,
            current_datetime,
            break_even_time_threshold,
            break_even_per_threshold
        )

    except ValueError:  # int(order.magic)
      pass

  @staticmethod
  def _check_if_break_even_can_be_placed(
      mt_client: MT_Client,
      order: Order,
      open_time: datetime,
      current_datetime: datetime,
      break_even_time_threshold: int,
      break_even_per_threshold: float,
      **kwargs
  ) -> bool:
    """Check if a break even can be placed."""
    _ = kwargs
    result = False
    # First check if a previous break even has been placed
    break_even_placed_buy = (
        order.order_type.buy and order.stop_loss > order.price
    )
    break_even_placed_sell = (
        order.order_type.sell and order.stop_loss < order.price
    )
    break_even_placed = break_even_placed_buy or break_even_placed_sell

    # Check if the time has reached a threshold to place a break even
    if not break_even_placed:
      reached_even_time_threshold = (
          current_datetime - open_time
      ).seconds > break_even_time_threshold

    # Check if the price has reached a threshold to place a break even
    if not break_even_placed:
      bid, ask = mt_client.get_bid_ask(order.symbol)
      price = (bid + ask) / 2
      percentage_reached = (
          price - order.stop_loss
      ) / (
          order.take_profit - order.stop_loss
      )
      price_reached_threshold = percentage_reached >= break_even_per_threshold

    if not break_even_placed and (
        price_reached_threshold or reached_even_time_threshold
    ):
      # We place a break even
      mt_client.place_break_even(order)
      result = True

    return result
