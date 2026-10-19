"""Runs the Cloudflare Pages Functions tests (tests/functions/*.mjs) under pytest."""
import os
import shutil
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.skipif(shutil.which('node') is None, reason='Node.js is needed to test the Cloudflare functions')
def test_cloudflare_functions():
    result = subprocess.run(
        ['node', '--no-warnings', '--test', os.path.join('tests', 'functions', 'cloudflare_functions.test.mjs')],
        cwd=ROOT, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout[-4000:] + result.stderr[-2000:]
