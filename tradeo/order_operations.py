"""Handle every type of trading operations."""
from enum import Enum


class OrderOperations(str, Enum):
  """Different order operations."""

  BUYLIMIT = 'buylimit'
  BUYSTOP = 'buystop'
  SELLLIMIT = 'selllimit'
  SELLSTOP = 'sellstop'
  BUY = 'buy'
  SELL = 'sell'
