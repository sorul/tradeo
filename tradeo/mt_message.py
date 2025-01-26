"""MT message classes."""
from datetime import datetime


class MT_MessageError:
  """Class for handling errors in MT messages."""

  def __init__(self, time: datetime, error_type: str, description: str):
    """Initialize the attributes."""
    self.time = time
    self.error_type = error_type
    self.description = description

  def __eq__(self, value: object) -> bool:
    """Check if the object is equal to another object."""
    return (
        isinstance(value, MT_MessageError)
        and str(self.time.year) == str(value.time.year)
        and str(self.time.month) == str(value.time.month)
        and str(self.time.day) == str(value.time.day)
        and str(self.time.hour) == str(value.time.hour)
        and str(self.time.minute) == str(value.time.minute)
        and str(self.time.second) == str(value.time.second)
        and self.error_type == value.error_type
        and self.description == value.description
    )

  def __str__(self) -> str:
    """Return a string representation."""
    return f'{self.time}: {self.error_type} - {self.description}'


class MT_MessageInfo:
  """Class for handling info messages in MT messages."""

  def __init__(self, time: datetime, message: str):
    """Initialize the attributes."""
    self.time = time
    self.message = message

  def __eq__(self, value: object) -> bool:
    """Check if the object is equal to another object."""
    return (
        isinstance(value, MT_MessageInfo)
        and str(self.time.year) == str(value.time.year)
        and str(self.time.month) == str(value.time.month)
        and str(self.time.day) == str(value.time.day)
        and str(self.time.hour) == str(value.time.hour)
        and str(self.time.minute) == str(value.time.minute)
        and str(self.time.second) == str(value.time.second)
        and self.message == value.message
    )

  def __str__(self) -> str:
    """Return a string representation."""
    return f'{self.time}: {self.message}'
