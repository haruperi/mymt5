import os
import time
import pytest
import configparser
from pathlib import Path

pytest.importorskip("pandas")

from mymt5.client import MT5Client
from mymt5.data import MT5Data
import MetaTrader5 as mt5


def _load_mt5_credentials():
    """Load MT5 credentials from config.ini (prefer demo), or env vars."""
    # ENV override wins
    env_login = os.getenv("MT5_LOGIN")
    env_password = os.getenv("MT5_PASSWORD")
    env_server = os.getenv("MT5_SERVER")
    env_path = os.getenv("MT5_TERMINAL_PATH")
    if env_login and env_password and env_server:
        return {
            "login": int(env_login),
            "password": env_password,
            "server": env_server,
            "path": env_path,
        }

    config_path = Path(__file__).resolve().parents[1] / "config.ini"
    if not config_path.exists():
        return None

    cp = configparser.ConfigParser()
    cp.read(config_path)

    section = None
    if cp.has_section("MT5_DEMO"):
        section = "MT5_DEMO"
    elif cp.has_section("MT5"):
        section = "MT5"

    if not section:
        return None

    # Keys may vary slightly; handle both 'path' and 'terminal_path'
    path_key = "terminal_path" if cp.has_option(section, "terminal_path") else "path"
    terminal_path = cp.get(section, path_key, fallback=None)

    try:
        return {
            "login": cp.getint(section, "login"),
            "password": cp.get(section, "password"),
            "server": cp.get(section, "server"),
            "path": terminal_path,
        }
    except Exception:
        return None


perf_enabled = os.getenv("ENABLE_PERF", "0") == "1"


@pytest.mark.performance
@pytest.mark.skipif(not perf_enabled, reason="Performance tests disabled by default. Set ENABLE_PERF=1 to run.")
def test_connection_speed_smoke():
    creds = _load_mt5_credentials()
    if not creds:
        pytest.skip("No MT5 credentials available (config.ini or env)")

    client = MT5Client(path=creds["path"]) if creds.get("path") else MT5Client()
    t0 = time.time()
    ok = client.initialize(login=creds["login"], password=creds["password"], server=creds["server"]) 
    dt = time.time() - t0
    assert ok is True
    assert dt < 2.0


@pytest.mark.performance
@pytest.mark.skipif(not perf_enabled, reason="Performance tests disabled by default. Set ENABLE_PERF=1 to run.")
def test_data_retrieval_speed_smoke():
    creds = _load_mt5_credentials()
    if not creds:
        pytest.skip("No MT5 credentials available (config.ini or env)")

    client = MT5Client(path=creds["path"]) if creds.get("path") else MT5Client()
    # Ensure connection
    assert client.initialize(login=creds["login"], password=creds["password"], server=creds["server"]) is True

    data = MT5Data(client=client)
    t0 = time.time()
    df = data.get_bars("EURUSD", timeframe=mt5.TIMEFRAME_M1, count=200)
    dt = time.time() - t0
    assert df is not None
    assert dt < 2.0


