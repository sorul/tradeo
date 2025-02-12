"""Common methods in trading strategies."""
from typing import List, Tuple, Dict
from pandas import Series, to_datetime, DataFrame
import numpy as np
from datetime import time, date

from tradeo.ohlc import OHLC
from tradeo.order_type import OrderType


def get_pip(symbol: str) -> float:
  """Return the pip value for symbol."""
  return 0.01 if 'JPY' in symbol else 0.0001


def get_pivots(
        data: np.ndarray,
        left: int,
        right: int,
        n_pivot: int,
        max_min: str
) -> List[Tuple[int, int]]:
  """Calculate the bar indices when a maximum or minimum occurs.

  left: number of greater/smaller bars to the left of the pivot
  right: number of greater/smaller bars to the right of the pivot
  n_pivot: number of pivots (tuples) to be found
  max_min: 'max' or 'min'

  Return [(value, index), (value, index), ..., n_pivot]
  """
  def getMax(data):
    m = max(data)
    i = data.index(m)
    return m, i

  def getMin(data):
    m = min(data)
    i = data.index(m)
    return m, i

  pivots = []  # [0] most recent
  data_list = list(data)
  size = left + right + 1
  a = -1 * (size + 1)
  b = -1
  d = data_list[a + 1:]
  m, i = getMax(d) if max_min == 'max' else getMin(d)
  if i == left and len(d) - 1 - i == right:
    pivots.append((m, len(d) - i - 1))
  while len(pivots) < n_pivot:
    d = data_list[a:b]
    if len(d) == size:
      m, i = getMax(d) if max_min == 'max' else getMin(d)
      if i == left and len(d) - 1 - i == right:
        pivots.append((m, -1 * b + right))
      a -= 1
      b -= 1
    else:
      break
  # Convert the indices to be prepared negatively
  # so that we can directly do for example: closes[-3]
  return [(i[0], -i[1] - 1) for i in pivots]


def EMA(
    data: np.ndarray,
    lookback: int,
    smoothing: int = 2
) -> List[float]:
  """Exponential Moving Average."""
  ema = [sum(data[:lookback]) / lookback]
  for price in data[lookback:]:
    ema.append(
        (price * (smoothing / (1 + lookback)))
        + ema[-1] * (1 - (smoothing / (1 + lookback)))
    )
  return ema


def RSI(data: np.ndarray, lookback: int) -> List[float]:
  """Relative Strength Index."""
  ret = Series(data).diff()
  up = []
  down = []
  for i in range(len(ret)):
    if ret[i] < 0:
      up.append(0)
      down.append(ret[i])
    else:
      up.append(ret[i])
      down.append(0)
  up_series = Series(up)
  down_series = Series(down).abs()
  up_ewm = up_series.ewm(com=lookback - 1, adjust=False).mean()
  down_ewm = down_series.ewm(com=lookback - 1, adjust=False).mean()
  rs = up_ewm / down_ewm
  return list(100 - (100 / (1 + rs)))


def SAR(  # noqa
  data: OHLC,
  af: float = 0.02,
  maxi: float = 0.2
) -> List[float]:
  """Calculate Simple Average Reversion."""
  high, low = data.high, data.low
  sig0, xpt0, af0 = True, high[0], af
  sar = [low[0] - (high - low).std()]
  for i in range(1, len(data)):
    sig1, xpt1, af1 = sig0, xpt0, af0
    l_min = min(low[i - 1], low[i])
    l_max = max(high[i - 1], high[i])
    if sig1:
      sig0 = low[i] > sar[-1]
      xpt0 = max(l_max, xpt1)
    else:
      sig0 = high[i] >= sar[-1]
      xpt0 = min(l_min, xpt1)
    if sig0 == sig1:
      sari = sar[-1] + (xpt1 - sar[-1]) * af1
      af0 = min(maxi, af1 + af)
      if sig0:
        af0 = af0 if xpt0 > xpt1 else af1
        sari = min(sari, l_min)
      else:
        af0 = af0 if xpt0 < xpt1 else af1
        sari = max(sari, l_max)
    else:
      af0 = af
      sari = xpt0
    sar.append(sari)
  return sar


def confirmation_pattern(data: OHLC, order_type: OrderType) -> bool:
  """Return True if different patterns are detected.

  https://s3.tradingview.com/z/zk1YPPgw_big.png
  https://www.tradingview.com/chart/EURUSD/zk1YPPgw-10-MOST-important-bar-patterns-to-profit-trade/
  """
  c1 = three_bar_reversal(data, order_type)
  c2 = pinbar_pattern(data, order_type)
  c3 = harami_pattern(data, order_type)
  return c1 or c2 or c3


def three_bar_reversal(data: OHLC, order_type: OrderType) -> bool:
  """Envelope Pattern.

  docs/images/buy_three_bar_reversal.png
  docs/images/sell_three_bar_reversal.png
  """
  opens = data.open
  highs = data.high
  lows = data.low
  closes = data.close
  if order_type.buy:
    return opens[-3] > closes[-3] and opens[-2] > closes[-2] and \
        opens[-1] < closes[-1] and lows[-3] > lows[-2] and \
        lows[-2] < lows[-1] and opens[-3] > highs[-2] and closes[-1] > highs[-2]
  else:
    return opens[-3] < closes[-3] and opens[-2] < closes[-2] and \
        opens[-1] > closes[-1] and highs[-3] < highs[-2] and \
        lows[-3] < lows[-2] and closes[-1] < lows[-2]


def pinbar_pattern(data: OHLC, order_type: OrderType) -> bool:
  """Pin-Bar Pattern.

  docs/images/buy_pinbar.png
  docs/images/sell_pinbar.png
  """
  opens = data.open
  highs = data.high
  lows = data.low
  closes = data.close
  if order_type.buy:
    upper_third = highs[-1] - (highs[-1] - lows[-1]) / 3
    body = abs(opens[-1] - closes[-1])
    lower_wick = opens[-1] - lows[-1]
    return (
        opens[-1] >= upper_third
    ) and (
        closes[-1] > upper_third
    ) and (
        lower_wick >= body * 3
    )
  else:
    lower_third = lows[-1] + (highs[-1] - lows[-1]) / 3
    body = abs(opens[-1] - closes[-1])
    upper_wick = highs[-1] - closes[-1]
    return (
        opens[-1] <= lower_third
    ) and (
        closes[-1] < lower_third
    ) and (
        upper_wick >= body * 3
    )


def harami_pattern(data: OHLC, order_type: OrderType) -> bool:
  """Harami Pattern.

  docs/images/buy_harami.png
  docs/images/sell_harami.png
  """
  opens = data.open
  highs = data.high
  lows = data.low
  closes = data.close
  if order_type.buy:
    return opens[-2] > closes[-2] and opens[-1] < closes[-1] and \
        highs[-1] < highs[-2] and lows[-1] > lows[-2]
  else:
    return opens[-2] < closes[-2] and opens[-1] > closes[-1] and \
        highs[-1] < highs[-2] and lows[-1] > lows[-2]


def calculate_poc_vah_val(
    ohlc: OHLC,
    session_start: str,
    session_end: str,
    value_area: float = 0.7
) -> Dict[date, Dict]:
  """
  Point of Control (POC), Value Area High (VAH), and Value Area Low (VAL).

  Args:
      ohlc (OHLC): An OHLC object containing market data.
      session_start (str): Start time of the session (e.g., '09:30').
      session_end (str): End time of the session (e.g., '16:00').
      value_area (float): Fraction of total volume for the value area.

  Returns:
      Dict: Dictionary with session dates as keys and POC, VAH, VAL as values.
  """
  session_start_time = to_datetime(session_start).time()
  session_end_time = to_datetime(session_end).time()

  dates = np.array([dt.date() for dt in ohlc.datetime])
  times = np.array([dt.time() for dt in ohlc.datetime])

  results = []

  for session_date in np.unique(dates):
    session_high, session_low, session_volume = _filter_session_data(
        dates, times, session_date, session_start_time, session_end_time,
        ohlc.high, ohlc.low, ohlc.volume
    )

    if len(session_high) == 0:
      continue

    price_bins, volume_profile = _calculate_volume_profile(
        session_high, session_low, session_volume
    )

    poc, vah, val = _calculate_poc_vah_val_from_profile(
        price_bins, volume_profile, value_area
    )

    results.append({
        'session_date': session_date,
        'POC': poc,
        'VAH': vah,
        'VAL': val
    })

  return {
      row['session_date']: {
          'poc': row['POC'], 'vah': row['VAH'], 'val': row['VAL']
      } for row in results
  }


def _filter_session_data(
    dates: np.ndarray,
    times: np.ndarray,
    session_date: np.datetime64,
    session_start_time: time,
    session_end_time: time,
    high: np.ndarray,
    low: np.ndarray,
    volume: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
  """
  Filter the data for a specific session.

  Args:
      dates: Array of dates.
      times: Array of times.
      session_date: Current session date.
      session_start_time: Start time of the session.
      session_end_time: End time of the session.
      high: High prices.
      low: Low prices.
      volume: Volume data.

  Returns:
      Filtered high, low, and volume data for the session.
  """
  session_mask = (dates == session_date) & \
                 (times >= session_start_time) & \
                 (times < session_end_time)
  return high[session_mask], low[session_mask], volume[session_mask]


def _calculate_volume_profile(
    session_high: np.ndarray,
    session_low: np.ndarray,
    session_volume: np.ndarray,
    num_bins: int = 100
) -> Tuple[np.ndarray, np.ndarray]:
  """
  Calculate the volume profile for a session.

  Args:
      session_high: High prices of the session.
      session_low: Low prices of the session.
      session_volume: Volume of the session.
      num_bins: Number of bins for the price range.

  Returns:
      Price bins and volume profile.
  """
  price_bins = np.linspace(session_low.min(), session_high.max(), num=num_bins)
  volume_profile = np.zeros(len(price_bins))

  for low, high, volume in zip(session_low, session_high, session_volume):
    price_range = np.linspace(low, high, num=10)
    vol_dist = volume / len(price_range)
    for price in price_range:
      idx = np.argmin(np.abs(price_bins - price))
      volume_profile[idx] += vol_dist

  return price_bins, volume_profile


def _calculate_poc_vah_val_from_profile(
    price_bins: np.ndarray,
    volume_profile: np.ndarray,
    value_area: float
) -> Tuple[float, float, float]:
  """
  Calculate POC, VAH, and VAL from a volume profile.

  Args:
      price_bins: Price bins.
      volume_profile: Volume profile.
      value_area: Fraction of total volume for the value area.

  Returns:
      POC, VAH, and VAL values.
  """
  poc_idx = np.argmax(volume_profile)
  poc = float(price_bins[poc_idx])

  sorted_volumes = sorted(volume_profile, reverse=True)
  cumulative_volume = np.cumsum(sorted_volumes)
  total_volume = cumulative_volume[-1]
  vah, val = poc, poc

  for idx, cum_vol in enumerate(cumulative_volume):
    if cum_vol >= total_volume * value_area:
      vah_idx = np.where(
          volume_profile == sorted_volumes[:idx + 1][-1])[0][0]
      vah = float(price_bins[vah_idx])
      break

  for idx, cum_vol in enumerate(cumulative_volume[::-1]):
    if cum_vol >= total_volume * value_area:
      val_idx = np.where(volume_profile == sorted_volumes[-(idx + 1)])[0][0]
      val = float(price_bins[val_idx])
      break

  return poc, vah, val


def calculate_heikin_ashi(data: OHLC) -> OHLC:
  """
  Calculate Heikin-Ashi OHLC data from an OHLC object.

  Args:
      data (OHLC): Input OHLC object with standard OHLC data.

  Returns:
      OHLC: New OHLC object with Heikin-Ashi calculated data.
  """
  # Calculate Heikin-Ashi close
  ha_close = (data.open + data.high + data.low + data.close) / 4

  # Calculate Heikin-Ashi open (iterative approach)
  ha_open = np.empty_like(ha_close)
  ha_open[0] = data.open[0]  # Initial value
  for i in range(1, len(ha_close)):
    ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2

  # Calculate Heikin-Ashi high and low
  ha_high = np.maximum.reduce([data.high, ha_open, ha_close])
  ha_low = np.minimum.reduce([data.low, ha_open, ha_close])

  # Create the Heikin-Ashi OHLC object
  return OHLC(
      df=DataFrame({
          'datetime': data.datetime,
          'open': ha_open,
          'high': ha_high,
          'low': ha_low,
          'close': ha_close,
          'tick_volume': data.volume
      }),
      open_column_name='open',
      high_column_name='high',
      low_column_name='low',
      close_column_name='close',
      datetime_column_name='datetime'
  )
