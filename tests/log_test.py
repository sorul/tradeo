from tradingbot.log import log


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
