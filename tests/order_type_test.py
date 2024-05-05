import pytest

from tradeo.order_type import get_order_type_from_str, OrderType
from tradeo.order_operations import OrderOperations


def test_get_order_type_from_str():
  ot = get_order_type_from_str('buylimit')
  assert ot == OrderType(buy=True, market=False)
  assert ot.value == OrderOperations.BUYLIMIT

  ot = get_order_type_from_str('buystop')
  assert ot == OrderType(buy=True, market=False)
  assert ot.value == OrderOperations.BUYSTOP

  ot = get_order_type_from_str('selllimit')
  assert ot == OrderType(buy=False, market=False)
  assert ot.value == OrderOperations.SELLLIMIT

  ot = get_order_type_from_str('sellstop')
  assert ot == OrderType(buy=False, market=False)
  assert ot.value == OrderOperations.SELLSTOP

  ot = get_order_type_from_str('buy')
  assert ot == OrderType(buy=True, market=True)
  assert ot.value == OrderOperations.BUY

  ot = get_order_type_from_str('sell')
  assert ot == OrderType(buy=False, market=True)
  assert ot.value == OrderOperations.SELL

  with pytest.raises(ValueError, match=r'Invalid order type'):
    ot = get_order_type_from_str('invalid')
