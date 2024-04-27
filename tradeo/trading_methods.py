"""Common methods in trading strategies."""
from typing import List, Tuple
from pandas import Series
from numpy import ndarray

from tradeo.ohlc import OHLC
from tradeo.order_type import OrderType


def get_pip(symbol: str) -> float:
  """Return the pip value for symbol."""
  return 0.01 if 'JPY' in symbol else 0.0001


def get_pivots(
        data: ndarray,
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
    data: ndarray,
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


def RSI(data: ndarray, lookback: int) -> List[float]:
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
