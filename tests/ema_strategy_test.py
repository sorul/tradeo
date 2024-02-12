from tradingbot.order import Order
from pandas import DataFrame
from tradingbot.ohlc import OHLC
from tradingbot.strategies.ema_strategy import EMA_strategy
import numpy as np


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
  strategy = EMA_strategy()
  assert isinstance(strategy.indicator(data, 'EURUSD'), Order)
