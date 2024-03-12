"""Class than extends EventHandler to provide basic functionality."""
from tradingbot.event_handlers.event_handler import EventHandler
from tradingbot.ohlc import OHLC
from tradingbot.strategies.strategy_factory import strategy_factory
from tradingbot.config import Config
from datetime import datetime
from tradingbot.mt_client import MT_Client


class BasicEventHandler(EventHandler):
  """This class only provides 'on_historical_data' event holder."""

  def __init__(self):
    """Initialize the attributes."""
    super().__init__('BasicEventHandler')

  def on_historical_data(
          self,
          symbol: str,
          data: OHLC
  ) -> None:
    """Handle the return of GET_HISTORICAL_DATA command."""
    now_date = datetime.now(Config.utc_timezone)
    mt_client = MT_Client()
    for strategy_name in Config.strategies:
      strategy = strategy_factory(strategy_name)
      possible_order = strategy.indicator(data, symbol, now_date)
      if possible_order and strategy.check_order_viability(possible_order):
        mt_client.create_new_order(possible_order)
