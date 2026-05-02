"""Historical trade records returned by MetaTrader.

This module models executed trade/deal history. A ``Trade`` is not used to
open, modify, or manage a live order; it represents a historical record that
has already been written by MetaTrader, including execution times, realized
financial result, commission, and swap.
"""
from datetime import datetime
from typing import Optional


class TradeTimes:
  """Class to hold trade timing information."""

  def __init__(
      self,
      deal_time: Optional[datetime] = None,
      execution_time: Optional[datetime] = None,
  ):
    """Initialize historical timing information for an executed trade."""
    self.deal_time = deal_time
    self.execution_time = execution_time


class TradeFinancials:
  """Class to hold trade financial details."""

  def __init__(
      self,
      deal_price: float,
      lots: float,
      pnl: float,
      commission: float,
      swap: float,
  ):
    """Initialize realized financial values for an executed trade."""
    self.deal_price = deal_price
    self.lots = lots
    self.pnl = pnl
    self.commission = commission
    self.swap = swap


class TradeMetadata:
  """Class to hold trade metadata."""

  def __init__(
      self,
      symbol: str,
      trade_type: str,
      entry: str,
      magic: int,
      comment: str,
  ):
    """Initialize identifying metadata for a historical trade record."""
    self.symbol = symbol
    self.trade_type = trade_type
    self.entry = entry
    self.magic = magic
    self.comment = comment


class Trade:
  """Class to hold trade data."""

  def __init__(
      self,
      metadata: TradeMetadata,
      financials: TradeFinancials,
      times: TradeTimes,
      ticket: int,
  ):
    """Initialize a historical trade/deal record.

    ``Trade`` instances are created from historical MetaTrader data. They are
    read-only domain objects for analysis, reconciliation, or duplicate-order
    checks, not commands that can be sent back to MetaTrader.
    """
    self._metadata = metadata
    self._financials = financials
    self._times = times
    self._ticket = ticket

  def __eq__(self, value: object) -> bool:
    """Check if the trade is equal to another trade."""
    return isinstance(value, Trade) and self.ticket == value.ticket

  def __str__(self) -> str:
    """Return a string representation of the trade."""
    return (
        f'Ticket: {self.ticket} - {self.comment} {self.symbol} '
        f'price: {self.deal_price} lots: {self.lots} '
        f'PNL: {self.pnl} commission: {self.commission} '
        f'swap: {self.swap} execution: {self.execution_time} '
        f'deal: {self.deal_time}'
    )

  @property
  def ticket(self) -> int:
    """Get the ticket."""
    return self._ticket

  @property
  def symbol(self) -> str:
    """Get the symbol."""
    return self._metadata.symbol

  @property
  def trade_type(self) -> str:
    """Get the trade type."""
    return self._metadata.trade_type

  @property
  def entry(self) -> str:
    """Get the entry type."""
    return self._metadata.entry

  @property
  def magic(self) -> int:
    """Get the magic number."""
    return self._metadata.magic

  @property
  def comment(self) -> str:
    """Get the comment."""
    return self._metadata.comment

  @property
  def lots(self) -> float:
    """Get the lots."""
    return self._financials.lots

  @property
  def deal_price(self) -> float:
    """Get the deal price."""
    return self._financials.deal_price

  @property
  def pnl(self) -> float:
    """Get the gain or loss."""
    return self._financials.pnl

  @property
  def commission(self) -> float:
    """Get the commission."""
    return self._financials.commission

  @property
  def swap(self) -> float:
    """Get the swap."""
    return self._financials.swap

  @property
  def deal_time(self) -> Optional[datetime]:
    """Get the deal time."""
    return self._times.deal_time

  @property
  def execution_time(self) -> Optional[datetime]:
    """Get the execution time."""
    return self._times.execution_time
