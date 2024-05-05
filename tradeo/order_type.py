"""Class to hold order type."""
from tradeo.order_operations import OrderOperations


class OrderType:
  """Class to hold order type."""

  def __init__(self, buy: bool, market: bool) -> None:
    """Order Type class for order_type attribute in the Order class.

    Args:
    - buy (bool): True if the order is a buy order,
    False if it is a sell order.
    - market (bool): True if the order is a market order,
    False if it is a pending order.
    """
    self.buy = buy
    self.sell = not buy
    self.market = market
    self.pending = not market

    self.__build()

  def __build(self) -> None:
    """Define the real order type.

    For non-market operations, "limit" type orders will be used by default,
    although they may automatically change to "stop" type orders when creating
    an order if the bid or ask value requires it.
    """
    if self.buy and self.market:
      self.value = OrderOperations.BUY
    elif self.buy and not self.market:
      self.value = OrderOperations.BUYLIMIT
    elif not self.buy and self.market:
      self.value = OrderOperations.SELL
    elif not self.buy and not self.market:
      self.value = OrderOperations.SELLLIMIT

  def __eq__(self, value: object) -> bool:
    """Check if the object is equal to another object."""
    return (
        isinstance(value, OrderType)
        and self.buy == value.buy
        and self.sell == value.sell
        and self.market == value.market
        and self.pending == value.pending
    )


def get_order_type_from_str(order_type_str: str) -> OrderType:
  """Get the order type object from a string."""
  if order_type_str == OrderOperations.BUYLIMIT:
    ot = OrderType(buy=True, market=False)
    ot.value = OrderOperations.BUYLIMIT
  elif order_type_str == OrderOperations.BUYSTOP:
    ot = OrderType(buy=True, market=False)
    ot.value = OrderOperations.BUYSTOP
  elif order_type_str == OrderOperations.SELLLIMIT:
    ot = OrderType(buy=False, market=False)
    ot.value = OrderOperations.SELLLIMIT
  elif order_type_str == OrderOperations.SELLSTOP:
    ot = OrderType(buy=False, market=False)
    ot.value = OrderOperations.SELLSTOP
  elif order_type_str == OrderOperations.BUY:
    ot = OrderType(buy=True, market=True)
    ot.value = OrderOperations.BUY
  elif order_type_str == OrderOperations.SELL:
    ot = OrderType(buy=False, market=True)
    ot.value = OrderOperations.SELL
  else:
    raise ValueError(f'Invalid order type: {order_type_str}')

  return ot
