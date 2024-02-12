"""EMA Strategy."""
from .strategy import Strategy
from typing import Union
from tradingbot.order import (Order,
                              MutableOrderDetails,
                              ImmutableOrderDetails,
                              OrderPrice,
                              OrderType)

from tradingbot.trading_methods import EMA, get_pivots
from tradingbot.ohlc import OHLC
from tradingbot.utils import create_magic_number
from tradingbot.forex_client import MT_Client


class EMA_strategy(Strategy):
  """Strategy based on EMAs and price tendency."""

  def __init__(self):
    """Initialize the attributes."""
    super().__init__('EMA_strategy')

  def indicator(
      self,
      ohlc: OHLC,
      symbol: str,
  ) -> Union[Order, None]:
    """Return an order if the strategy is triggered."""
    # Calculate the EMAs
    ema_20 = EMA(ohlc.close, 20)
    ema_50 = EMA(ohlc.close, 50)

    # Calculate the pivots
    p = get_pivots(ohlc.high, left=6, right=3, n_pivot=2, max_min='max')
    max_pivot_1 = p[0][0]  # most recent
    max_pivot_2 = p[1][0]

    p = get_pivots(ohlc.low, left=6, right=3, n_pivot=2, max_min='min')
    min_pivot_1 = p[0][0]  # most recent
    min_pivot_2 = p[1][0]

    # Check the conditions
    upper_tendency = max_pivot_1 > max_pivot_2 and min_pivot_1 > min_pivot_2
    lower_tendency = not upper_tendency and (
        max_pivot_1 < max_pivot_2) and (min_pivot_1 < min_pivot_2)

    # Obtain common features
    magic = create_magic_number()
    pip = MT_Client.get_pip(symbol)

    if ema_20[-1] >= ema_50[-1] and upper_tendency:
      return Order(
          MutableOrderDetails(
              OrderPrice(
                  take_profit=ema_20[-1] + 20 * pip,
                  stop_loss=ema_50[-1] - 10 * pip
              ), symbol),
          ImmutableOrderDetails(OrderType.BUY, magic, self.strategy_name),
      )
    elif lower_tendency:
      return Order(
          MutableOrderDetails(
              OrderPrice(
                  take_profit=ema_20[-1] - 20 * pip,
                  stop_loss=ema_50[-1] + 10 * pip
              ), symbol),
          ImmutableOrderDetails(OrderType.SELL, magic, self.strategy_name),
      )

    return None
