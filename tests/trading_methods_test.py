import tradingbot.trading_methods as tm
from pandas import Series, DataFrame
import numpy as np


def test_get_pivots():
  data_with_max_pivot = Series([1, 1, 10, 1, 1])
  left = 2
  right = 2
  n_pivot = 2
  max_min = 'max'

  # max_pivots -> [[10, -3]]
  max_pivots = tm.get_pivots(
      data_with_max_pivot, left, right, n_pivot, max_min)

  assert len(max_pivots) == 1
  assert data_with_max_pivot.iloc[max_pivots[0][1]] == max_pivots[0][0]

  data_with_min_pivot = Series([20, 10, 1, 10, 20])
  left = 2
  right = 2
  n_pivot = 2
  max_min = 'min'

  # max_pivots -> [[10, -3]]
  min_pivots = tm.get_pivots(
      data_with_min_pivot, left, right, n_pivot, max_min)

  assert len(min_pivots) == 1
  assert data_with_min_pivot.iloc[min_pivots[0][1]] == min_pivots[0][0]


def test_EMA():
  assert tm.EMA(Series([1, 2, 3]), lookback=3) == [2.0]
  assert tm.EMA(Series([0, 2]), lookback=2) == tm.EMA(Series([2]), lookback=2)


def test_RSI():
  assert np.isnan(tm.RSI(Series([1, 2, 3]), 3)[0])
  assert tm.RSI(Series([1, 2, 3]), 3)[-2:] == [100, 100]


def test_SAR():
  data = DataFrame({'high': [1, 2, 3], 'low': [1, 2, 3]})
  assert tm.SAR(data) == [1.0, 1.0, 1.04]
  data = DataFrame({'high': [0, 0, 3], 'low': [0, 0, 100]})
  assert tm.SAR(data) == [
      -56.0029761113937, -54.88291658916582, -53.78525825738251
  ]


def test_buy_three_bar_reversal():
  data = DataFrame({
      'high': [5, 3, 6],
      'open': [4, 2, 1],
      'close': [2, 1, 5],
      'low': [1, 0, 0.5]
  })
  assert tm.three_bar_reversal(data, 'buy')


def test_sell_three_bar_reversal():
  data = DataFrame({
      'high': [5, 6, 5.5],
      'open': [2, 4, 5],
      'close': [4, 5, 1],
      'low': [1, 3, 0]
  })
  assert tm.three_bar_reversal(data, 'sell')


def test_buy_pinbar():
  data = DataFrame({
      'high': [6],
      'open': [4],
      'close': [5],
      'low': [0]
  })
  assert tm.pinbar_pattern(data, 'buy')


def test_sell_pinbar():
  data = DataFrame({
      'high': [6],
      'open': [2],
      'close': [1],
      'low': [0]
  })
  assert tm.pinbar_pattern(data, 'sell')


def test_buy_harami():
  data = DataFrame({
      'high': [6, 5],
      'open': [5, 1],
      'close': [1, 4],
      'low': [0, 0.5]
  })
  assert tm.harami_pattern(data, 'buy')


def test_sell_harami():
  data = DataFrame({
      'high': [6, 5.5],
      'open': [1, 5],
      'close': [5, 2],
      'low': [0, 1]
  })
  assert tm.harami_pattern(data, 'sell')
