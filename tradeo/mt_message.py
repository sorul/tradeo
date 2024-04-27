"""MT message classes."""
from tradeo.utils import string_to_date_utc
from tradeo.config import Config


class MT_MessageError:
  """Class for handling errors in MT messages."""

  def __init__(self, time: str, error_type: str, description: str):
    """Initialize the attributes."""
    self.time = string_to_date_utc(
        time,
        date_format='%Y.%m.%d %H:%M:%S',
        from_timezone=Config.broker_timezone
    )
    self.error_type = error_type
    self.description = description

  def __eq__(self, value: object) -> bool:
    """Check if the object is equal to another object."""
    return (
        isinstance(value, MT_MessageError)
        and str(self.time) == str(value.time)
        and self.error_type == value.error_type
        and self.description == value.description
    )


class MT_MessageInfo:
  """Class for handling info messages in MT messages."""

  def __init__(self, time: str, message: str):
    """Initialize the attributes."""
    self.time = string_to_date_utc(
        time,
        date_format='%Y.%m.%d %H:%M:%S',
        from_timezone=Config.broker_timezone
    )
    self.message = message

  def __eq__(self, value: object) -> bool:
    """Check if the object is equal to another object."""
    return (
        isinstance(value, MT_MessageInfo)
        and str(self.time) == str(value.time)
        and self.message == value.message
    )
