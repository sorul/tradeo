"""Strategy factory."""
from tradingbot.strategies.strategy import Strategy
from tradingbot.log import log


def strategy_factory(strategy: str) -> Strategy:
  """Given a strategy name, return the corresponding strategy object."""
  from tradingbot.strategies.ema_strategy import (EMA_strategy)

  for s in [EMA_strategy()]:
    if s.strategy_name in strategy or strategy in s.strategy_name:
      return s

  error_message = f'Not such {strategy} strategy!'
  log.error(error_message)
  raise Exception(error_message)
