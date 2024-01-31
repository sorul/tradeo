"""Class to hold order data."""


class OrderPrice:
  """Class to hold order price."""

  def __init__(self, price, stop_loss, take_profit):
    """Initialize the attributes."""
    self.price = price
    self.stop_loss = stop_loss
    self.take_profit = take_profit


class MutableOrderDetails:
  """Class to hold order details."""

  def __init__(
      self,
      prices: OrderPrice,
      symbol: str,
      lots: float,
      expiration: int
  ):
    """Initialize the attributes."""
    self._prices = prices
    self.symbol = symbol
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

  def __init__(self, order_type, magic, comment):
    """Initialize the attributes."""
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
  magic (int): Magic number
  comment (str): Order comment
  expiration (int): Expiration time given as timestamp in seconds.
      Can be zero if the order should not have an expiration time.

  """

  def __init__(
      self,
      details: MutableOrderDetails,
      metadata: ImmutableOrderDetails
  ):
    """Initialize the attributes."""
    self._details = details
    self._metadata = metadata

  @property
  def symbol(self) -> str:
    """Get the symbol."""
    return self._details.symbol

  @property
  def order_type(self) -> str:
    """Get the order type."""
    return self._metadata.order_type

  @property
  def lots(self) -> float:
    """Get the lots."""
    return self._details.lots

  @property
  def price(self) -> float:
    """Get the price."""
    return self._details.price

  @property
  def stop_loss(self) -> float:
    """Get the stop loss."""
    return self._details.stop_loss

  @property
  def take_profit(self) -> float:
    """Get the take profit."""
    return self._details.take_profit

  @property
  def magic(self) -> str:
    """Get the magic number."""
    return self._metadata.magic

  @property
  def comment(self) -> str:
    """Get the comment."""
    return self._metadata.comment

  @property
  def expiration(self) -> int:
    """Get the expiration."""
    return self._details.expiration
