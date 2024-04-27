"""Class than extends EventHandler to provide basic functionality."""
from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from tradeo.event_handlers.event_handler import EventHandler
from tradeo.strategies.basic_strategy import BasicStrategy
from tradeo.config import Config
if TYPE_CHECKING:
  from tradeo.ohlc import OHLC
  from tradeo.mt_client import MT_Client


class BasicEventHandler(EventHandler):
  """This class only provides 'on_historical_data' event holder."""

  def __init__(self):
    """Initialize the attributes."""
    super().__init__('BasicEventHandler')

  def on_historical_data(
          self,
          mt_client: MT_Client,
          symbol: str,
          data: OHLC
  ) -> None:
    """Handle the return of GET_HISTORICAL_DATA command."""
    now_date = datetime.now(Config.utc_timezone)
    strategy = BasicStrategy()
    possible_order = strategy.indicator(data, symbol, now_date)
    if possible_order and strategy.check_order_viability(
            mt_client, possible_order):
      mt_client.create_new_order(possible_order)
