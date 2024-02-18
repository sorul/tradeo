"""EventHandler factory."""
from tradingbot.event_handlers.event_handler import EventHandler
from tradingbot.log import log


def event_handler_factory(event_handler: str) -> EventHandler:
  """Given a event_handler name, return the corresponding event_handler."""
  from tradingbot.event_handlers.basic_event_handler import (BasicEventHandler)

  for s in [BasicEventHandler()]:
    if (
            s.event_handler_name in event_handler
    ) or (
        event_handler in s.event_handler_name
    ):
      return s

  error_message = f'Not such {event_handler} strategy!'
  log.error(error_message)
  raise Exception(error_message)
