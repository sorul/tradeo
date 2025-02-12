"""OHLC class to encapsulate OHLC data."""

from pandas import DataFrame, to_datetime
import numpy as np
from typing import Optional
import pytz


class OHLC:
  """OHLC class for financial market data."""

  def __init__(
      self,
      df: DataFrame,
      open_column_name: str = 'open',
      high_column_name: str = 'high',
      low_column_name: str = 'low',
      close_column_name: str = 'close',
      volume_column_name: Optional[str] = 'tick_volume',
      datetime_column_name: Optional[str] = None,
      convert_to_utc: Optional[str | pytz.BaseTzInfo] = None,
  ):
    """
    Initialize OHLC attributes from a DataFrame.

    Args:
        df (DataFrame): A DataFrame containing OHLC data.
        open_column_name (str): Column name for the 'open' prices.
        high_column_name (str): Column name for the 'high' prices.
        low_column_name (str): Column name for the 'low' prices.
        close_column_name (str): Column name for the 'close' prices.
        volume_column_name (Optional[str]): Column name for the 'volume' data.
        datetime_column_name (Optional[str]): Column name for the 'datetime'
                data. If None, assumes the index is datetime.
        convert_to_utc (Optional[str | pytz.BaseTzInfo]): If provided, assumes
        the original timezone and converts the datetime to UTC.

    Raises:
        ValueError: If required columns or datetime data are missing
                                                              in the DataFrame.
    """
    df = df.copy()

    # Handle datetime column or index
    if datetime_column_name and datetime_column_name not in df.columns:
      raise ValueError(
        f'Datetime column "{datetime_column_name}" not found in DataFrame.')
    df = df.set_index(datetime_column_name) if datetime_column_name else df

    try:
      df.index = to_datetime(df.index)
    except Exception as e:
      raise ValueError(
          'The index could not be converted to datetime. '
          'Ensure it is properly formatted.'
      ) from e

    if convert_to_utc:
      if isinstance(convert_to_utc, str):
        df.index = df.index.tz_localize(convert_to_utc).tz_convert('UTC')
      elif isinstance(convert_to_utc, pytz.BaseTzInfo):
        df.index = df.index.tz_localize(convert_to_utc).tz_convert('UTC')
      else:
        raise TypeError((
          'convert_to_utc must be a pytz.BaseTzInfo'
          ' or a str representing a timezone.'
        ))

    # Convert datetime to Python datetime objects
    self.datetime = np.array(df.index.to_pydatetime())
    self.open = df[open_column_name].to_numpy()
    self.high = df[high_column_name].to_numpy()
    self.low = df[low_column_name].to_numpy()
    self.close = df[close_column_name].to_numpy()
    self.volume = (
        df[volume_column_name].to_numpy()
        if volume_column_name and volume_column_name in df.columns
        else np.zeros_like(self.open)
    )

  def __len__(self):
    """Return the number of OHLC entries."""
    return len(self.open)

  def to_dataframe(self) -> DataFrame:
    """
    Convert the OHLC object back to a DataFrame.

    Returns:
        DataFrame: A DataFrame containing the OHLC data.
    """
    data = {
        'datetime': self.datetime,
        'open': self.open,
        'high': self.high,
        'low': self.low,
        'close': self.close,
    }
    if self.volume.size > 0:
      data['volume'] = self.volume
    return DataFrame(data).set_index('datetime')

  def summary(self) -> str:
    """
    Generate a textual summary of the OHLC data.

    Returns:
        str: A summary string with basic statistics.
    """
    return (
        f"OHLC Summary:\n"
        f"- Number of entries: {len(self)}\n"
        f"- Open (min: {self.open.min()}, max: {self.open.max()})\n"
        f"- High (min: {self.high.min()}, max: {self.high.max()})\n"
        f"- Low (min: {self.low.min()}, max: {self.low.max()})\n"
        f"- Close (min: {self.close.min()}, max: {self.close.max()})\n"
        f"- Volume: {'Available' if self.volume.size > 0 else 'Not available'}"
    )
