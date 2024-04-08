from unittest.mock import patch
import os

from tradingbot.context_managers.blocker import Blocker


@patch('tradingbot.files.get_default_path')
def test_blocker(mock_default_path, tmp_path):

  # Make data_path() return the temporary directory
  mock_default_path.return_value = tmp_path

  name = ''
  with Blocker('test') as blocker:
    name = blocker.name
    assert os.path.exists(tmp_path / name)

  assert not os.path.exists(tmp_path / name)
