"""
Shared pytest fixtures for Bubbsy Start Page & OSINT Hub test suite.
"""

import os
import tempfile

# Keep the test run's accounts in a throwaway database, never the real one in ~/.bubbsy.
os.environ.setdefault('BUBBSY_DB_PATH', os.path.join(tempfile.mkdtemp(prefix='bubbsy-test-'), 'accounts.db'))

import pytest
import threading
import urllib.request
import time
import socket
import server

def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

@pytest.fixture(scope="session")
def live_server():
    """Session-level live server fixture on port 7777."""
    host = "127.0.0.1"
    port = server.PORT
    if not is_port_open(host, port):
        t = threading.Thread(target=server.run_server, daemon=True)
        t.start()
        for _ in range(20):
            if is_port_open(host, port):
                break
            time.sleep(0.1)
    yield f"http://{host}:{port}"
