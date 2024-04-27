"""Class to hold order data."""
from tradeo.order_type import OrderType


class OrderPrice:
  """Class to hold order price."""

  def __init__(
      self,
      price: float = 0,
      stop_loss: float = 0,
      take_profit: float = 0
  ):
    """Initialize the attributes."""
    self.price = price
    self.stop_loss = stop_loss
    self.take_profit = take_profit


class MutableOrderDetails:
  """Class to hold order details."""

  def __init__(
      self,
      prices: OrderPrice,
      lots: float = 0.01,
      expiration: int = 0
  ):
    """Initialize the attributes."""
    self._prices = prices
    self.lots = lots
    self.expiration = expiration

  @property
  def price(self):
    """Get the entry price."""
    return self._prices.price

  @property
  def stop_loss(self):
    """Get the stop loss."""
    return self._prices.stop_loss

  @property
  def take_profit(self):
    """Get the take profit."""
    return self._prices.take_profit


class ImmutableOrderDetails:
  """Class to hold order metadata."""

  def __init__(
          self,
          symbol: str,
          order_type: OrderType,
          magic: str,
          comment: str,
  ):
    """Initialize the attributes."""
    self.symbol = symbol
    self.order_type = order_type
    self.magic = magic
    self.comment = comment


class Order:
  """Class to hold order data.

  symbol (str): Symbol for which an order should be opened.
  order_type (str): Order type. Can be one of:
      'buy', 'sell', 'buylimit', 'selllimit', 'buystop', 'sellstop'
  lots (float): Volume in lots
  price (float): Price of the (pending) order. Can be zero
      for market orders.
  stop_loss (float): SL as absolute price. Can be zero
      if the order should not have an SL.
  take_profit (float): TP as absolute price. Can be zero
      if the order should not have a TP.
  magic (int): Used to identify the order.
      Could be used to specify the timestamp as well.
  comment (str): Order comment
  expiration (int): Expiration time given as timestamp in seconds.
      Can be zero if the order should not have an expiration time.

  """

  def __init__(
      self,
      mutable_details: MutableOrderDetails,
      immutable_details: ImmutableOrderDetails,
      ticket: int = 0,
      pnl: float = 0
  ):
    """Initialize the attributes."""
    self._mutable_details = mutable_details
    self._immutable_details = immutable_details
    self._ticket = ticket  # it would not be available until the order be filled
    self._pnl = pnl  # it would not be available until the order be filled

  def __eq__(self, __value: object) -> bool:
    """Check if the order is equal to another order."""
    return isinstance(__value, Order) and self.ticket == __value.ticket

  def __str__(self) -> str:
    """Return a string representation of the order."""
    return f'{self.comment} {self.symbol} {self.price} {self.magic}'

  @property
  def symbol(self) -> str:
    """Get the symbol."""
    return self._immutable_details.symbol

  @property
  def order_type(self) -> OrderType:
    """Get the order type."""
    return self._immutable_details.order_type

  @property
  def lots(self) -> float:
    """Get the lots."""
    return self._mutable_details.lots

  @property
  def price(self) -> float:
    """Get the price."""
    return self._mutable_details.price

  @property
  def stop_loss(self) -> float:
    """Get the stop loss."""
    return self._mutable_details.stop_loss

  @property
  def take_profit(self) -> float:
    """Get the take profit."""
    return self._mutable_details.take_profit

  @property
  def magic(self) -> str:
    """Get the magic number."""
    return self._immutable_details.magic

  @property
  def comment(self) -> str:
    """Get the comment."""
    return self._immutable_details.comment

  @property
  def expiration(self) -> int:
    """Get the expiration."""
    return self._mutable_details.expiration

  @property
  def ticket(self) -> int:
    """Get the ticket."""
    return self._ticket

  @property
  def pnl(self) -> float:
    """Get the gain or loss."""
    return self._pnl

  def risk_benefit(self) -> float:
    """Get the risk benefit."""
    a = abs(self.take_profit - self.price)
    b = abs(self.price - self.stop_loss)
    return a / b if b > 0 else 0
