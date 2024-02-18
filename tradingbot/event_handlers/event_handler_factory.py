"""EventHandler factory."""
from .event_handler import EventHandler
from .basic_event_handler import BasicEventHandler


def event_handler_factory(event_handler: str) -> EventHandler:
  """Given a event_handler name, return the corresponding event_handler."""
  for s in [BasicEventHandler()]:
    if (
            s.event_handler_name in event_handler
    ) or (
        event_handler in s.event_handler_name
    ):
      return s

  raise Exception(f'Not such {event_handler} strategy!')
