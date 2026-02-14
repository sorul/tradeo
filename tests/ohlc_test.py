from datetime import datetime
import numpy as np
import pandas as pd
import pytest
import pytz

from tradeo.ohlc import OHLC


def test_ohlc_init_with_datetime_column_and_len():
  df = pd.DataFrame({
      'datetime': ['2024-01-01 10:00', '2024-01-01 11:00'],
      'open': [1.0, 2.0],
      'high': [1.5, 2.5],
      'low': [0.8, 1.8],
      'close': [1.2, 2.2],
      'volume': [100, 200],
  })

  ohlc = OHLC(df, datetime_column_name='datetime')

  assert len(ohlc) == 2
  assert np.array_equal(ohlc.open, np.array([1.0, 2.0]))
  assert np.array_equal(ohlc.high, np.array([1.5, 2.5]))
  assert np.array_equal(ohlc.low, np.array([0.8, 1.8]))
  assert np.array_equal(ohlc.close, np.array([1.2, 2.2]))
  assert np.array_equal(ohlc.volume, np.array([100, 200]))
  assert isinstance(ohlc.datetime[0], datetime)


def test_ohlc_uses_zero_volume_when_column_is_missing():
  df = pd.DataFrame({
      'datetime': ['2024-01-01 10:00', '2024-01-01 11:00'],
      'open': [1.0, 2.0],
      'high': [1.5, 2.5],
      'low': [0.8, 1.8],
      'close': [1.2, 2.2],
  })

  ohlc = OHLC(df, datetime_column_name='datetime')

  assert np.array_equal(ohlc.volume, np.array([0.0, 0.0]))


def test_ohlc_convert_to_utc_with_string_timezone():
  df = pd.DataFrame({
      'datetime': ['2024-01-01 10:00'],
      'open': [1.0],
      'high': [1.5],
      'low': [0.8],
      'close': [1.2],
  })

  ohlc = OHLC(
      df,
      datetime_column_name='datetime',
      convert_to_utc='Europe/Madrid',
  )

  assert ohlc.datetime[0] == pd.Timestamp('2024-01-01 09:00:00+00:00')


def test_ohlc_convert_to_utc_with_pytz_timezone():
  df = pd.DataFrame({
      'datetime': ['2024-06-01 10:00'],
      'open': [1.0],
      'high': [1.5],
      'low': [0.8],
      'close': [1.2],
  })

  ohlc = OHLC(
      df,
      datetime_column_name='datetime',
      convert_to_utc=pytz.timezone('Europe/Madrid'),
  )

  assert ohlc.datetime[0] == pd.Timestamp('2024-06-01 08:00:00+00:00')


def test_ohlc_to_dataframe_contains_expected_columns():
  df = pd.DataFrame({
      'datetime': ['2024-01-01 10:00', '2024-01-01 11:00'],
      'open': [1.0, 2.0],
      'high': [1.5, 2.5],
      'low': [0.8, 1.8],
      'close': [1.2, 2.2],
      'volume': [100, 200],
  })

  ohlc = OHLC(df, datetime_column_name='datetime')
  result = ohlc.to_dataframe()

  assert list(result.columns) == ['open', 'high', 'low', 'close', 'volume']
  assert result.index.name == 'datetime'
  assert len(result) == 2


def test_ohlc_summary_contains_basic_sections():
  df = pd.DataFrame({
      'datetime': ['2024-01-01 10:00', '2024-01-01 11:00'],
      'open': [1.0, 2.0],
      'high': [1.5, 2.5],
      'low': [0.8, 1.8],
      'close': [1.2, 2.2],
      'volume': [100, 200],
  })

  ohlc = OHLC(df, datetime_column_name='datetime')
  summary = ohlc.summary()

  assert 'OHLC Summary' in summary
  assert 'Number of entries: 2' in summary
  assert 'Volume: Available' in summary


def test_ohlc_raises_when_datetime_column_does_not_exist():
  df = pd.DataFrame({
      'open': [1.0],
      'high': [1.5],
      'low': [0.8],
      'close': [1.2],
  })

  with pytest.raises(ValueError, match='Datetime column "dt" not found'):
    OHLC(df, datetime_column_name='dt')


def test_ohlc_raises_when_index_cannot_be_converted_to_datetime():
  df = pd.DataFrame({
      'open': [1.0, 2.0],
      'high': [1.5, 2.5],
      'low': [0.8, 1.8],
      'close': [1.2, 2.2],
  }, index=['not-a-date', 'still-not-a-date'])

  with pytest.raises(ValueError, match='The index could not be converted'):
    OHLC(df)


def test_ohlc_raises_when_convert_to_utc_type_is_invalid():
  df = pd.DataFrame({
      'datetime': ['2024-01-01 10:00'],
      'open': [1.0],
      'high': [1.5],
      'low': [0.8],
      'close': [1.2],
  })

  with pytest.raises(TypeError, match='convert_to_utc must be'):
    OHLC(df, datetime_column_name='datetime', convert_to_utc=123)
