"""This class blocks the execution writing a .block file."""
from tradeo.files import write_file, remove_file, file_exists


class Blocker:
  """Blocker class."""

  def __init__(self, name: str) -> None:
    """Initialize the Blocker."""
    self.name = f'{name}.block'

  def is_blocked(self) -> bool:
    """Check if the execution is blocked."""
    return file_exists(self.name)

  def __enter__(self) -> 'Blocker':
    """Blocker enter."""
    write_file(self.name)
    return self

  def __exit__(self, exc_type: str, exc_value: str, traceback: str) -> bool:
    """Blocker exit."""
    _, _, _ = exc_type, exc_value, traceback
    remove_file(self.name)
    return True
