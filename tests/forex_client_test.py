from pathlib import Path
from unittest.mock import patch, Mock
from tradingbot.forex_client import MT_Client


@patch('subprocess.run')
def test_command_file_exist(mock_run):

  client = MT_Client(start=False)
  path = client.path_commands_prefix

  # Configure the mock to return predefined results
  file1_str = f'{path}0.txt:<:123|GET_HISTORIC_DATA|GBPNZD,M5,1704701519:>'
  file2_str = f'{path}1.txt:<:456|GET_HISTORIC_DATA|GBPNZD,M5,1704701519:>'
  mock_run.return_value = Mock(
      returncode=0, stdout=f'{file1_str}\n{file2_str}')

  result = client.command_file_exist('GBPNZD')
  assert result == [Path(f'{path}0.txt'), Path(f'{path}1.txt')]
