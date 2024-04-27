"""Abstract class for executables."""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from tradeo.mt_client import MT_Client


class Executable(ABC):
  """This class should not be instantiated."""

  @abstractmethod
  def entry_point(self) -> None:
    """Entry point of the executable."""

  @abstractmethod
  def main(self, mt_client: MT_Client) -> None:
    """Execute the executable."""

  @abstractmethod
  def handle_trades(self, mt_client: MT_Client) -> None:
    """Handle the existing trades."""

  @abstractmethod
  def handle_new_historical_data(
          self,
          mt_client: MT_Client,
          utc_date: datetime,
          execution_time: timedelta
  ) -> None:
    """Handle the new historical data."""

  @abstractmethod
  def is_locked(self) -> bool:
    """Return True if the executable is running."""

  @abstractmethod
  def check_time_viability(self) -> bool:
    """Check if the time is viable to execute the executable."""

  @abstractmethod
  def finish(self, mt_client: MT_Client) -> None:
    """Finish the executable."""
