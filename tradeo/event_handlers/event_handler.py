"""Parent class for event handlers."""
from __future__ import annotations
from typing import List, Dict, TYPE_CHECKING
from abc import ABC

if TYPE_CHECKING:
  from tradeo.order import Order
  from tradeo.ohlc import OHLC
  from tradeo.mt_client import MT_Client


class EventHandler(ABC):
  """This class should not be instantiated."""

  def __init__(self, event_handler_name: str):
    """Initialize the attributes."""
    self.event_handler_name = event_handler_name

  def on_tick(
      self,
      mt_client: MT_Client,
      symbol: str,
      bid: float,
      ask: float
  ) -> None:
    """Handle the return of SUBSCRIBE_SYMBOLS command."""
    return None

  def on_bar_data(
      self,
      mt_client: MT_Client,
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
          mt_client: MT_Client,
          symbol: str,
          data: OHLC
  ) -> None:
    """Handle the return of GET_HISTORICAL_DATA command."""
    return None

  def on_historical_trades(
      self,
      mt_client: MT_Client
  ) -> None:
    """Handle the return of GET_HISTORICAL_TRADES command."""
    return None

  def on_message(
          self,
          mt_client: MT_Client,
          message: List[str]) -> None:
    """Handle when a new message is received."""
    return None

  def on_order_event(
          self,
          mt_client: MT_Client,
          account_info: Dict,
          open_orders: List[Order]
  ) -> None:
    """Handle when a new order event or removed order is received."""
    return None
