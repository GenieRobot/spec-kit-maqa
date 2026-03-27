"""
Tests for multi-agent configuration options: auto_push and qa_cadence.

Tests cover:
- Persisting auto_push and qa_cadence in init-options.json
- Default values when flags are not provided
- Validation of qa_cadence values
- auto_push defaults to False
"""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from specify_cli import app, save_init_options


class TestSaveMultiAgentOptions:
    """Tests for save_init_options with auto_push and qa_cadence."""

    def test_save_auto_push_true(self, tmp_path: Path):
        opts = {"auto_push": True, "ai": "claude"}
        save_init_options(tmp_path, opts)

        saved = json.loads((tmp_path / ".specify/init-options.json").read_text())
        assert saved["auto_push"] is True

    def test_save_auto_push_false(self, tmp_path: Path):
        opts = {"auto_push": False, "ai": "claude"}
        save_init_options(tmp_path, opts)

        saved = json.loads((tmp_path / ".specify/init-options.json").read_text())
        assert saved["auto_push"] is False

    def test_save_qa_cadence_per_feature(self, tmp_path: Path):
        opts = {"qa_cadence": "per_feature", "ai": "claude"}
        save_init_options(tmp_path, opts)

        saved = json.loads((tmp_path / ".specify/init-options.json").read_text())
        assert saved["qa_cadence"] == "per_feature"

    def test_save_qa_cadence_batch_end(self, tmp_path: Path):
        opts = {"qa_cadence": "batch_end", "ai": "claude"}
        save_init_options(tmp_path, opts)

        saved = json.loads((tmp_path / ".specify/init-options.json").read_text())
        assert saved["qa_cadence"] == "batch_end"


class TestMultiAgentDefaults:
    """Tests that defaults are applied when flags are not provided."""

    def test_auto_push_defaults_to_false(self, tmp_path: Path, monkeypatch):
        def _fake_download(project_path, *args, **kwargs):
            Path(project_path).mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr("specify_cli.download_and_extract_template", _fake_download)

        runner = CliRunner()
        result = runner.invoke(app, ["init", str(tmp_path / "proj"), "--ai", "claude", "--ignore-agent-tools"])
        assert result.exit_code == 0

        saved = json.loads((tmp_path / "proj" / ".specify/init-options.json").read_text())
        assert saved["auto_push"] is False

    def test_qa_cadence_defaults_to_per_feature(self, tmp_path: Path, monkeypatch):
        def _fake_download(project_path, *args, **kwargs):
            Path(project_path).mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr("specify_cli.download_and_extract_template", _fake_download)

        runner = CliRunner()
        result = runner.invoke(app, ["init", str(tmp_path / "proj"), "--ai", "claude", "--ignore-agent-tools"])
        assert result.exit_code == 0

        saved = json.loads((tmp_path / "proj" / ".specify/init-options.json").read_text())
        assert saved["qa_cadence"] == "per_feature"

    def test_auto_push_flag_sets_true(self, tmp_path: Path, monkeypatch):
        def _fake_download(project_path, *args, **kwargs):
            Path(project_path).mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr("specify_cli.download_and_extract_template", _fake_download)

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["init", str(tmp_path / "proj"), "--ai", "claude", "--auto-push", "--ignore-agent-tools"],
        )
        assert result.exit_code == 0

        saved = json.loads((tmp_path / "proj" / ".specify/init-options.json").read_text())
        assert saved["auto_push"] is True

    def test_qa_cadence_batch_end_flag(self, tmp_path: Path, monkeypatch):
        def _fake_download(project_path, *args, **kwargs):
            Path(project_path).mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr("specify_cli.download_and_extract_template", _fake_download)

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["init", str(tmp_path / "proj"), "--ai", "claude", "--qa-cadence", "batch_end", "--ignore-agent-tools"],
        )
        assert result.exit_code == 0

        saved = json.loads((tmp_path / "proj" / ".specify/init-options.json").read_text())
        assert saved["qa_cadence"] == "batch_end"


class TestQaCadenceValidation:
    """Tests for --qa-cadence CLI validation."""

    def test_invalid_qa_cadence_rejected(self, tmp_path: Path):
        runner = CliRunner()
        result = runner.invoke(
            app,
            ["init", str(tmp_path / "proj"), "--ai", "claude", "--qa-cadence", "always"],
        )
        assert result.exit_code == 1
        assert "Invalid --qa-cadence" in result.output

    def test_valid_qa_cadence_per_feature(self, tmp_path: Path, monkeypatch):
        def _fake_download(project_path, *args, **kwargs):
            Path(project_path).mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr("specify_cli.download_and_extract_template", _fake_download)

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["init", str(tmp_path / "proj"), "--ai", "claude", "--qa-cadence", "per_feature", "--ignore-agent-tools"],
        )
        assert result.exit_code == 0
        assert "Invalid --qa-cadence" not in (result.output or "")

    def test_valid_qa_cadence_batch_end(self, tmp_path: Path, monkeypatch):
        def _fake_download(project_path, *args, **kwargs):
            Path(project_path).mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr("specify_cli.download_and_extract_template", _fake_download)

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["init", str(tmp_path / "proj"), "--ai", "claude", "--qa-cadence", "batch_end", "--ignore-agent-tools"],
        )
        assert result.exit_code == 0
        assert "Invalid --qa-cadence" not in (result.output or "")
