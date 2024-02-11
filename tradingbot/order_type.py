"""Trading operation class."""
from enum import Enum


class OrderType(str, Enum):
  """Define the different operations in trading."""

  BUY = 'buy'
  SELL = 'sell'
  BUYLIMIT = 'buylimit'
  SELLLIMIT = 'selllimit'
  BUYSTOP = 'buystop'
  SELLSTOP = 'sellstop'
