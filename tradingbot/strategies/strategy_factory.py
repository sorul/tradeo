"""Strategy factory."""
from .strategy import Strategy
from .ema_strategy import EMA_strategy


def strategy_factory(strategy: str) -> Strategy:
  """Given a strategy name, return the corresponding strategy object."""
  for s in [EMA_strategy()]:
    if s.strategy_name in strategy or strategy in s.strategy_name:
      return s

  raise Exception(f'Not such {strategy} strategy!')
