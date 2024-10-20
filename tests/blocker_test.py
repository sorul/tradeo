import os
import time
import pytest
from unittest import mock
from tradeo.blocker import Blocker


@pytest.fixture
def _cleanup_lockfile():
  lockfile = '/tmp/tradeo_test.lock'
  yield
  if os.path.exists(lockfile):
    os.remove(lockfile)


@pytest.mark.usefixtures('_cleanup_lockfile')
def test_blocker_creates_lockfile():
  """Test that the lock file is created."""
  with Blocker('/tmp/tradeo_test.lock'):
    assert os.path.exists(
        '/tmp/tradeo_test.lock'), 'The lock file was not created.'


@pytest.mark.usefixtures('_cleanup_lockfile')
@mock.patch('psutil.pid_exists', return_value=True)
def test_blocker_prevents_execution_if_lock_exists(mock):
  """Test that execution is prevented if a lock file already exists.

  And the process is still running.
  """
  # We create a lock file manually
  with open('/tmp/tradeo_test.lock', 'w') as f:
    f.write('1234,{}'.format(time.time()))

  # Simulating process still alive with mock
  with pytest.raises(SystemExit):
    with Blocker('/tmp/tradeo_test.lock'):
      pass


@pytest.mark.usefixtures('_cleanup_lockfile')
def test_blocker_removes_lockfile_on_exit():
  """Test that the lock file is removed upon exiting the context."""
  with Blocker('/tmp/tradeo_test.lock'):
    pass
  assert not os.path.exists(
      '/tmp/tradeo_test.lock'), 'The lock file was not removed.'


@pytest.mark.usefixtures('_cleanup_lockfile')
@mock.patch('psutil.pid_exists', return_value=False)
def test_blocker_removes_stale_lockfile(mock):
  """Test - Stale lock file is removed if the process no longer exists."""
  # We create a lock file with a non-existent PID and old timestamp
  with open('/tmp/tradeo_test.lock', 'w') as f:
    f.write('1234,{}'.format(time.time() - 600))  # 10 minutes ago

  # We run Blocker, it should remove the stale lock file
  with Blocker('/tmp/tradeo_test.lock', timeout=300):
    assert os.path.exists(
        '/tmp/tradeo_test.lock'), 'The lock file should have been recreated.'


@pytest.mark.usefixtures('_cleanup_lockfile')
@mock.patch('psutil.pid_exists', return_value=True)
def test_blocker_does_not_remove_recent_lockfile(mock):
  """Test that a recent lock file is not removed if the process still exists."""
  # We create a lock file with an existing PID and recent timestamp
  with open('/tmp/tradeo_test.lock', 'w') as f:
    f.write('1234,{}'.format(time.time() - 100))  # Less than 5 minutes ago

  # We run Blocker, it should detect that the file is not stale
  with pytest.raises(SystemExit):
    with Blocker('/tmp/tradeo_test.lock', timeout=300):
      pass


@pytest.mark.usefixtures('_cleanup_lockfile')
def test_blocker_handles_invalid_lockfile_format():
  """Test that a lock file with an invalid format is considered stale."""
  # We create a lock file with an invalid format
  with open('/tmp/tradeo_test.lock', 'w') as f:
    f.write('invalid_content')

  # We run Blocker, it should remove the lock file due to invalid format
  with Blocker('/tmp/tradeo_test.lock'):
    assert os.path.exists(
        '/tmp/tradeo_test.lock'), 'The lock file should have been recreated.'
