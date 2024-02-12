"""OHLC class to encapsulate OHLC data."""
from pandas import DataFrame


class OHLC:
  """OHLC class."""

  def __init__(self, df: DataFrame):
    """Initialize the attributes."""
    self.open = df['open'].to_numpy()
    self.high = df['high'].to_numpy()
    self.low = df['low'].to_numpy()
    self.close = df['close'].to_numpy()

  def __len__(self):
    """Return the length of the OHLC data."""
    return len(self.open)
