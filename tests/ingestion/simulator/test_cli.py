from typer.testing import CliRunner
from top_songs.ingestion.simulator.cli import simulator_app

runner = CliRunner()

def test_generate_master_help():
    result = runner.invoke(simulator_app, ["generate-master", "--help"])
    assert result.exit_code == 0
    assert "--num-songs" in result.output

def test_run_help():
    result = runner.invoke(simulator_app, ["run", "--help"])
    assert result.exit_code == 0
    assert "--historical" in result.output

def test_generate_master_invalid_format():
    result = runner.invoke(simulator_app, ["generate-master", "--format", "xml"])
    assert result.exit_code != 0
    assert "Format must be 'csv' or 'json'" in result.output

def test_run_negative_threads():
    result = runner.invoke(simulator_app, ["run", "--threads", "-2"])
    assert result.exit_code != 0
    assert "must be a positive integer" in result.output 