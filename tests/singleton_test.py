from tradingbot.singleton import Singleton


class Test_Singleton(metaclass=Singleton):
  """Dummy class that is a singleton."""


class Test_Not_Singleton():
  """Dummy class that is not a singleton."""


def test_singleton():
  s1 = Test_Singleton()
  s2 = Test_Singleton()

  ns1 = Test_Not_Singleton()
  ns2 = Test_Not_Singleton()

  assert id(s1) == id(s2)
  assert id(ns1) != id(ns2)
