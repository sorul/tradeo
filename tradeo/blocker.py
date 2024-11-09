"""This class blocks execution by writing a .block file."""
import os
import time
import psutil

from tradeo.log import log


class Blocker:
  """
  A class used to block execution by writing a .block file.

  This class creates a lock file to prevent multiple instances
  of a script from running simultaneously.
  It checks if the lock file is stale based on a timeout and the existence
  of the process whose PID is in the file.
  """

  def __init__(self, lockfile='/tmp/tradeo.lock', timeout=300):
    """
    Initialize the class with the lock file path and a timeout.

    If the lock file is older than the timeout,it will be automatically removed.
    it will be automatically removed.
    :param lockfile: The path to the lock file.
    :param timeout: Maximum time in seconds that the lock
    file is considered valid.
    """
    self.lockfile = lockfile
    self.timeout = timeout

  def is_stale(self):
    """
    Check if the lock file is stale.

    Checks if the lock file is stale
    or if the process whose PID is in the file no longer exists.
    """
    is_stale = True
    # Check if the lock file exists
    if not os.path.exists(self.lockfile):
      return False

    try:
      # Read the PID and creation time of the lock file
      with open(self.lockfile, 'r') as lock_fh:
        content = lock_fh.read().strip().split(',')
        if len(content) != 2:
          # If it doesn't have the expected format, consider it stale
          is_stale = True

        pid, timestamp = int(content[0]), float(content[1])

        # Check if the process with the PID still exists
        if is_stale and psutil.pid_exists(pid):
          # If the process still exists, the file is not stale
          is_stale = False

        # If the file is too old, consider it stale
        if not is_stale and time.time() - timestamp > self.timeout:
          is_stale = True
    except ValueError:
      is_stale = True

    return is_stale

  def __enter__(self):
    """
    Enters the context and creates the lock file.

    If the file already exists and is not stale, the script exits.
    If the file is stale, it is removed and a new one is created.
    """
    # First, check if the lock file exists
    if os.path.exists(self.lockfile):
      # If the file exists, check if it's stale
      if not self.is_stale():
        # If it's not stale, exit the program
        log.warning('Another instance is running. Exiting...')
        exit(0)
      else:
        # If the file is stale, remove it
        log.warning('The lock file is stale. Removing it...')
        os.remove(self.lockfile)

    # If we get here, it's because the file didn't exist
    # or was stale and we removed it. Create the new lock file
    with open(self.lockfile, 'w') as lock_fh:
      lock_fh.write(f'{os.getpid()},{time.time()}')

  def __exit__(self, _exc_type, _exc_val, _exc_tb):
    """Exit the context and remove the lock file."""
    if os.path.exists(self.lockfile):
      os.remove(self.lockfile)
