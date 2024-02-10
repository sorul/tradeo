"""Trading operation class."""
from enum import Enum


class Operation(str, Enum):
  """Define the different operations in trading."""

  BUY = 'buy'
  SELL = 'sell'
