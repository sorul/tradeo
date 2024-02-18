"""Parent class for event handlers."""
from tradingbot.ohlc import OHLC
from typing import List, Dict
from abc import ABC


class EventHandler(ABC):
  """This class should not be instantiated."""

  def __init__(self, event_handler_name: str):
    """Initialize the attributes."""
    self.event_handler_name = event_handler_name

  def on_tick(
      self,
      symbol: str,
      bid: float,
      ask: float
  ) -> None:
    """Handle the return of SUBSCRIBE_SYMBOLS command."""
    return None

  def on_bar_data(
      self,
      symbol: str,
      time_frame: str,
      time: str,
      ohlc: OHLC,
      tick_volume: float
  ) -> None:
    """Handle the return of SUBSCRIBE_SYMBOLS_BAR_DATA command."""
    return None

  def on_historical_data(
          self,
          symbol: str,
          data: OHLC
  ) -> None:
    """Handle the return of GET_HISTORICAL_DATA command."""
    return None

  def on_historical_trades(
      self
  ) -> None:
    """Handle the return of GET_HISTORICAL_TRADES command."""
    return None

  def on_message(self, message: List[str]) -> None:
    """Handle when a new message is received."""
    return None

  def on_order_event(self, account_info: Dict, open_orders: Dict) -> None:
    """Handle the return of an order event."""
    return None
