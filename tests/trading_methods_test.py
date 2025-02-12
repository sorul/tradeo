import pytest
import pandas as pd
import numpy as np
from pathlib import Path

import tradeo.trading_methods as tm
from tradeo.ohlc import OHLC
from tradeo.order_type import OrderType
from tradeo.files import try_load_json
from tradeo.paths import resources_test_path


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
  data = OHLC(pd.DataFrame({
      'high': [1, 2, 3],
      'low': [1, 2, 3],
      'close': [0, 0, 0],
      'open': [0, 0, 0],
  }))
  assert tm.SAR(data) == [1.0, 1.0, 1.04]
  data = OHLC(pd.DataFrame({
      'high': [0, 0, 3],
      'low': [0, 0, 100],
      'close': [0, 0, 0],
      'open': [0, 0, 0],
  }))
  assert tm.SAR(data) == [
      -45.72623851673007, -44.81171374639547, -43.91547947146756
  ]


def test_buy_three_bar_reversal():
  data = OHLC(pd.DataFrame({
      'high': [5, 3, 6],
      'open': [4, 2, 1],
      'close': [2, 1, 5],
      'low': [1, 0, 0.5]
  }))
  assert tm.three_bar_reversal(data, OrderType(buy=True, market=True))


def test_sell_three_bar_reversal():
  data = OHLC(pd.DataFrame({
      'high': [5, 6, 5.5],
      'open': [2, 4, 5],
      'close': [4, 5, 1],
      'low': [1, 3, 0]
  }))
  assert tm.three_bar_reversal(data, OrderType(buy=False, market=True))


def test_buy_pinbar():
  data = OHLC(pd.DataFrame({
      'high': [6],
      'open': [4],
      'close': [5],
      'low': [0]
  }))
  assert tm.pinbar_pattern(data, OrderType(buy=True, market=True))


def test_sell_pinbar():
  data = OHLC(pd.DataFrame({
      'high': [6],
      'open': [2],
      'close': [1],
      'low': [0]
  }))
  assert tm.pinbar_pattern(data, OrderType(buy=False, market=True))


def test_buy_harami():
  data = OHLC(pd.DataFrame({
      'high': [6, 5],
      'open': [5, 1],
      'close': [1, 4],
      'low': [0, 0.5]
  }))
  assert tm.harami_pattern(data, OrderType(buy=True, market=True))


def test_sell_harami():
  data = OHLC(pd.DataFrame({
      'high': [6, 5.5],
      'open': [1, 5],
      'close': [5, 2],
      'low': [0, 1]
  }))
  assert tm.harami_pattern(data, OrderType(buy=False, market=True))


def test_get_pip():
  assert tm.get_pip('GBPUSD') == 0.0001
  assert tm.get_pip('USDJPY') == 0.01


def test_calculate_poc_vah_val_ohlc():
  data = {
      'datetime': [
          '2023-01-01 09:00', '2023-01-01 10:00', '2023-01-01 11:00',
          '2023-01-01 12:00', '2023-01-01 13:00'
      ],
      'open': [1.1, 1.2, 1.3, 1.4, 1.5],
      'high': [1.5, 1.6, 1.7, 1.8, 1.9],
      'low': [1.0, 1.1, 1.2, 1.3, 1.4],
      'close': [1.3, 1.4, 1.5, 1.6, 1.7],
      'tick_volume': [100, 200, 300, 400, 500],
  }
  df = pd.DataFrame(data)
  df['datetime'] = pd.to_datetime(df['datetime'])

  ohlc = OHLC(
      df=df,
      datetime_column_name='datetime'
  )

  session_start = '09:00'
  session_end = '12:00'
  value_area = 0.7

  result = tm.calculate_poc_vah_val(
      ohlc=ohlc,
      session_start=session_start,
      session_end=session_end,
      value_area=value_area
  )

  expected_result = {
      pd.Timestamp('2023-01-01').date(): {
          'poc': pytest.approx(1.197979797979798, 0.01),
          'vah': pytest.approx(1.098989898989899, 0.01),
          'val': pytest.approx(1.007070707070707, 0.01),
      }
  }

  assert result == expected_result


def test_calculate_heikin_ashi():
  data = {
      'datetime': [
          '2023-01-01 09:00', '2023-01-01 10:00', '2023-01-01 11:00'
      ],
      'open': [1.0, 1.1, 1.2],
      'high': [1.2, 1.3, 1.4],
      'low': [0.9, 1.0, 1.1],
      'close': [1.1, 1.2, 1.3],
      'tick_volume': [100, 200, 300]
  }
  df = pd.DataFrame(data)
  df['datetime'] = pd.to_datetime(df['datetime'])

  ohlc = OHLC(
      df=df,
      datetime_column_name='datetime',
      convert_to_utc='Europe/Madrid'
  )

  heikin_ashi = tm.calculate_heikin_ashi(ohlc)

  expected_ha_open = np.array([1.0, 1.025, 1.0875])
  expected_ha_close = np.array([1.05, 1.15, 1.25])
  expected_ha_high = np.array([1.2, 1.3, 1.4])
  expected_ha_low = np.array([0.9, 1.0, 1.0875])
  expected_ha_volume = np.array([100, 200, 300])

  assert np.allclose(heikin_ashi.open, expected_ha_open)
  assert np.allclose(heikin_ashi.close, expected_ha_close)
  assert np.allclose(heikin_ashi.high, expected_ha_high)
  assert np.allclose(heikin_ashi.low, expected_ha_low)
  assert np.allclose(heikin_ashi.volume, expected_ha_volume)


def _load_data() -> OHLC:
  file_path = Path(
    f'{resources_test_path()}/AgentFiles/Historical_Data_SP500.json')
  data = try_load_json(file_path)
  df = pd.DataFrame.from_dict(
        data['SP500_M5'], orient='index')  # type: ignore
  return OHLC(
      df=df,
  )
