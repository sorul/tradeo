from tradingbot.paths import config_path, data_path
import tradingbot.files as files
from pathlib import Path
import tempfile


def test_get_successful_symbols():
  path = data_path().joinpath('successful_symbols.txt')
  with open(path, 'a') as file:
    file.write('EURUSD\n')
    file.write('USDCAD\n')
  symbols = files.get_successful_symbols()
  assert isinstance(symbols, list)
  assert len(symbols) > 0


def test_file_exists():
  with tempfile.NamedTemporaryFile() as temp_file:
    # File exists
    temp_directory = Path(tempfile.mkstemp()[1])
    assert files.file_exists(temp_file.name, temp_directory)

  # File does not exist
  assert not files.file_exists('invalid.txt', config_path())


def test_try_load_json():
  with tempfile.NamedTemporaryFile() as temp_file:
    file = Path(temp_file.name)
    with open(file, 'w') as f:
      f.write('{"test": "test"}')
    data = files.try_load_json(file)
    assert data['test'] == 'test'


def test_try_remove_file():
  with tempfile.TemporaryDirectory() as tmp_dir:

    # Create the temporary file inside the temporary directory
    temp_file = Path(tmp_dir) / "temp.txt"
    temp_file.touch()

    # Make sure it exists before trying to remove it
    assert temp_file.exists()

    # Try to remove it
    assert files.try_remove_file(temp_file)

    # Validate that it no longer exists
    assert not temp_file.exists()
