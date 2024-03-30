from tradingbot.order import Order
from pandas import DataFrame
from tradingbot.ohlc import OHLC
from tradingbot.strategies.basic_strategy import BasicStrategy
import numpy as np
from datetime import datetime


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
  strategy = BasicStrategy()
  assert isinstance(strategy.indicator(data, 'EURUSD', datetime.now()), Order)
