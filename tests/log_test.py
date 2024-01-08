from tradingbot.log import Log, log


def test_info():
  log.info('Testing info')
  assert True


def test_debug():
  log.debug('Testing debug')
  assert True


def test_warning():
  log.warning('Testing warning')
  assert True


def test_error():
  log.error('Testing error')
  assert True


def test_singleton():
  log1 = Log()
  log2 = Log()

  class NotSingleton():
    pass
  ns1 = NotSingleton()
  ns2 = NotSingleton()

  assert id(log1) == id(log2)
  assert id(ns1) != id(ns2)
