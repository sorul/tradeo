"""Abstract class for strategies."""
from __future__ import annotations  # for TYPE_CHECKING
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Union, TYPE_CHECKING, Optional

from tradeo.config import Config
from tradeo.log import log
from tradeo.trading_methods import get_pip
if TYPE_CHECKING:
  from tradeo.order import Order
  from tradeo.ohlc import OHLC
  from tradeo.mt_client import MT_Client


class Strategy(ABC):
  """This class should not be instantiated.

  Only ``indicator`` is mandatory for subclasses. The remaining concrete
  methods provide a default implementation and are intended as extension
  points that users can override to adapt the strategy lifecycle to their
  own execution logic.
  """

  def __init__(
          self,
          strategy_name: str,
          mt_client: MT_Client
  ):
    """Initialize the attributes."""
    self.strategy_name = strategy_name
    self.mt_client = mt_client

  @abstractmethod
  def indicator(
          self,
          ohlc: OHLC,
          symbol: str,
          date: datetime,
          **kwargs,
  ) -> Union[Order, None]:
    """Return an order if the strategy is triggered."""

  def check_order_viability(
      self,
      order: Order,
      min_risk_profit: float = 1.5,
      date: Optional[datetime] = None,
      **kwargs,
  ) -> bool:
      """Check if the order is viable."""
      _ = kwargs
      if date is None:
          date = datetime.now(Config.utc_timezone)

      symbol = order.symbol
      orders = [o for o in self.mt_client.open_orders if o.symbol == symbol]
      c1 = len(orders) == 0
      c2 = order.risk_benefit() > min_risk_profit
      c3 = date.hour not in [22, 23, 0]
      return c1 and c2 and c3

  def handle_pending_orders(
      self,
      order: Order,
      time_threshold: int = 3600,
      **kwargs,
  ) -> None:
    """Handle limit orders based on the time threshold.

    Subclasses can override this default management behavior.
    """
    _ = kwargs
    try:
      open_time = datetime.fromtimestamp(
          int(order.magic)).astimezone(Config.utc_timezone)
      current_datetime = datetime.now(Config.utc_timezone)
      if (current_datetime - open_time).total_seconds() > time_threshold:
        self.mt_client.send_close_orders_by_magic_command(order.magic)
        log.debug(f'Close order {order.magic} due to time threshold')
    except ValueError:  # int(order.magic)
      pass

  def handle_filled_orders(
      self,
      order: Order,
      time_threshold: int = 3600 * 24,
      break_even_time_threshold: int = 3600 * 12,
      break_even_per_threshold: float = 0.75,
      **kwargs,
  ) -> None:
    """Handle filled orders by closing them or placing a break even.

    Subclasses can override this default management behavior.
    """
    _ = kwargs
    try:
      open_time = datetime.fromtimestamp(
          int(order.magic)).astimezone(Config.utc_timezone)
      current_datetime = datetime.now(Config.utc_timezone)

      # Check if the order can be closed based on the time threshold
      if (current_datetime - open_time).total_seconds() > time_threshold:
        self.mt_client.send_close_orders_by_magic_command(order.magic)
        log.debug(f'Close order {order.magic} due to time threshold')

      # Check if a break even can be placed
      else:
        self._check_if_break_even_can_be_placed(
            order,
            open_time,
            current_datetime,
            break_even_time_threshold,
            break_even_per_threshold
        )

    except ValueError:  # int(order.magic)
      pass

  def _check_if_break_even_can_be_placed(
      self,
      order: Order,
      open_time: datetime,
      current_datetime: datetime,
      break_even_time_threshold: int,
      break_even_per_threshold: float,
      **kwargs,
  ) -> bool:
    """Check if a break even can be placed."""
    _ = kwargs
    result = False
    # First check if a previous break even has been placed
    break_even_placed_buy = (
        order.order_type.buy and order.stop_loss >= order.price
    )
    break_even_placed_sell = (
        order.order_type.sell and order.stop_loss <= order.price
    )
    break_even_placed = break_even_placed_buy or break_even_placed_sell

    if break_even_placed:
      return result

    bid, ask = self.mt_client.get_bid_ask(order.symbol)

    # Break even can only be placed when the close price is in profit.
    if not self._price_is_in_profit(order, bid, ask):
      return result

    # Check if the time has reached a threshold to place a break even
    reached_even_time_threshold = (
        current_datetime - open_time
    ).total_seconds() > break_even_time_threshold

    # Check if the price has reached a threshold to place a break even
    price_reached_threshold = (
        self._profit_path_percentage_reached(order, bid, ask) >=
        break_even_per_threshold
    )

    if price_reached_threshold or reached_even_time_threshold:
      if price_reached_threshold:
        reason = 'Price percentage reached'
      else:
        reason = 'Time threshold reached'
      if self._break_even_stop_already_crossed(order, bid, ask):
        log.debug(
            f'Break even was not placed for order {order.ticket} because '
            f'the current close price already crossed the break even stop. '
            f'{reason}'
        )
      else:
        result = True
        self.mt_client.place_break_even(order, log_comment=reason)

    return result

  def _price_is_in_profit(
      self,
      order: Order,
      bid: float,
      ask: float,
  ) -> bool:
    """Return whether the order can currently be closed in profit."""
    close_price = bid if order.order_type.buy else ask
    if not close_price:
      return False
    if order.order_type.buy:
      return close_price > order.price
    return close_price < order.price

  def _profit_path_percentage_reached(
      self,
      order: Order,
      bid: float,
      ask: float,
  ) -> float:
    """Return how much of the entry-to-take-profit path was reached."""
    close_price = bid if order.order_type.buy else ask
    profit_path = abs(order.take_profit - order.price)
    if profit_path == 0:
      return 0
    reached_path = (
        close_price - order.price
        if order.order_type.buy
        else order.price - close_price
    )
    return reached_path / profit_path

  def _break_even_stop_already_crossed(
      self,
      order: Order,
      bid: float,
      ask: float,
  ) -> bool:
    """Return whether placing break even would create an invalid stop."""
    close_price = bid if order.order_type.buy else ask
    if not close_price:
      return False
    break_even = self._get_break_even_price(order)
    if order.order_type.buy:
      return close_price <= break_even
    return close_price >= break_even

  @staticmethod
  def _get_break_even_price(order: Order) -> float:
    """Return the stop-loss price used by MT_Client.place_break_even."""
    pip = get_pip(order.symbol)
    if order.order_type.buy:
      return order.price + pip
    return order.price - pip
