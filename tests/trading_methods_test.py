import tradeo.trading_methods as tm
from pandas import DataFrame
import numpy as np
from tradeo.ohlc import OHLC
from tradeo.order_type import OrderType


def test_get_pivots():
  data_with_max_pivot = np.array([1, 1, 10, 1, 1])
  left = 2
  right = 2
  n_pivot = 2
  max_min = 'max'

  # max_pivots -> [[10, -3]]
  max_pivots = tm.get_pivots(
      data_with_max_pivot, left, right, n_pivot, max_min)

  assert len(max_pivots) == 1
  assert data_with_max_pivot[max_pivots[0][1]] == max_pivots[0][0]

  data_with_min_pivot = np.array([20, 10, 1, 10, 20])
  left = 2
  right = 2
  n_pivot = 2
  max_min = 'min'

  # max_pivots -> [[10, -3]]
  min_pivots = tm.get_pivots(
      data_with_min_pivot, left, right, n_pivot, max_min)

  assert len(min_pivots) == 1
  assert data_with_min_pivot[min_pivots[0][1]] == min_pivots[0][0]


def test_EMA():
  assert tm.EMA(np.array([1, 2, 3]), lookback=3) == [2.0]
  assert tm.EMA(np.array([0, 2]), lookback=2) == tm.EMA(np.array([2]),
                                                        lookback=2)


def test_RSI():
  assert np.isnan(tm.RSI(np.array([1, 2, 3]), 3)[0])
  assert tm.RSI(np.array([1, 2, 3]), 3)[-2:] == [100, 100]


def test_SAR():
  data = OHLC(DataFrame({
      'high': [1, 2, 3],
      'low': [1, 2, 3],
      'close': [0, 0, 0],
      'open': [0, 0, 0],
  }))
  assert tm.SAR(data) == [1.0, 1.0, 1.04]
  data = OHLC(DataFrame({
      'high': [0, 0, 3],
      'low': [0, 0, 100],
      'close': [0, 0, 0],
      'open': [0, 0, 0],
  }))
  assert tm.SAR(data) == [
      -45.72623851673007, -44.81171374639547, -43.91547947146756
  ]


def test_buy_three_bar_reversal():
  data = OHLC(DataFrame({
      'high': [5, 3, 6],
      'open': [4, 2, 1],
      'close': [2, 1, 5],
      'low': [1, 0, 0.5]
  }))
  assert tm.three_bar_reversal(data, OrderType(buy=True, market=True))


def test_sell_three_bar_reversal():
  data = OHLC(DataFrame({
      'high': [5, 6, 5.5],
      'open': [2, 4, 5],
      'close': [4, 5, 1],
      'low': [1, 3, 0]
  }))
  assert tm.three_bar_reversal(data, OrderType(buy=False, market=True))


def test_buy_pinbar():
  data = OHLC(DataFrame({
      'high': [6],
      'open': [4],
      'close': [5],
      'low': [0]
  }))
  assert tm.pinbar_pattern(data, OrderType(buy=True, market=True))


def test_sell_pinbar():
  data = OHLC(DataFrame({
      'high': [6],
      'open': [2],
      'close': [1],
      'low': [0]
  }))
  assert tm.pinbar_pattern(data, OrderType(buy=False, market=True))


def test_buy_harami():
  data = OHLC(DataFrame({
      'high': [6, 5],
      'open': [5, 1],
      'close': [1, 4],
      'low': [0, 0.5]
  }))
  assert tm.harami_pattern(data, OrderType(buy=True, market=True))


def test_sell_harami():
  data = OHLC(DataFrame({
      'high': [6, 5.5],
      'open': [1, 5],
      'close': [5, 2],
      'low': [0, 1]
  }))
  assert tm.harami_pattern(data, OrderType(buy=False, market=True))


def test_get_pip():
  assert tm.get_pip('GBPUSD') == 0.0001
  assert tm.get_pip('USDJPY') == 0.01
