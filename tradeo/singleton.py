"""Singleton definition."""


class Singleton(type):
  """Singleton metaclass."""

  _instances = {}

  def __call__(cls, *args, **kwargs):
    """Prevent multiple instances."""
    if cls not in cls._instances:
      cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    return cls._instances[cls]
