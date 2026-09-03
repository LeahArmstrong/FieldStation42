import asyncio
import importlib.util
import pathlib
from types import SimpleNamespace
from unittest.mock import patch


def load_summary_module():
    path = pathlib.Path(__file__).parents[1] / "fs42/fs42_server/api/summary.py"
    spec = importlib.util.spec_from_file_location("test_summary_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


summary = load_summary_module()


def test_public_config_exposes_only_time_format_and_has_a_safe_default():
    manager = SimpleNamespace(server_conf={"time_format": "%-I:%M %p", "tmdb_api_key": "secret"})
    with patch.object(summary, "StationManager", return_value=manager):
        assert asyncio.run(summary.get_public_config()) == {"time_format": "%-I:%M %p"}

    manager.server_conf["time_format"] = ""
    with patch.object(summary, "StationManager", return_value=manager):
        assert asyncio.run(summary.get_public_config()) == {"time_format": "%H:%M"}
