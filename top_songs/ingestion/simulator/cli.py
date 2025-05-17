import typer
from typer import Option, BadParameter
from top_songs.ingestion.simulator.commands import generate_master_data_command, run_simulation_command
from datetime import datetime
from top_songs.core.config.logger import setup_logging

setup_logging()

simulator_app = typer.Typer(name="simulate", help="Generate and simulate song play data.") 

def validate_positive(ctx, param, value):
    if value is not None and value < 0:
        raise BadParameter(f"{param.name} must be a positive integer.")
    return value

def validate_datetime(ctx, param, value):
    if value is not None:
        try:
            datetime.fromisoformat(value)
        except Exception:
            raise BadParameter(f"{param.name} must be a valid ISO datetime string.")
    return value

def validate_format(ctx, param, value):
    if value not in ("csv", "json"):
        raise BadParameter("Format must be 'csv' or 'json'.")
    return value

@simulator_app.command("generate-master")
def generate_master(
    output_dir: str = Option("data/master/", help="Directory to store master data files."),
    num_songs: int = Option(1000, help="Number of song records to generate.", callback=validate_positive),
    num_users: int = Option(5000, help="Number of user records to generate.", callback=validate_positive),
    num_locations: int = Option(100, help="Number of location/region records to generate.", callback=validate_positive),
    format: str = Option("csv", help="Output format for master data (csv or json).", callback=validate_format),
):
    """
    Generate master data for songs, users, and locations.
    """
    generate_master_data_command(
        output_dir=output_dir,
        num_songs=num_songs,
        num_users=num_users,
        num_locations=num_locations,
        format=format,
    )

@simulator_app.command("run")
def run(
    master_data_dir: str = Option("data/master/", help="Directory to load master data from."),
    api_endpoint: str = Option("http://localhost:8000/play", help="The URL of the API endpoint to post play events."),
    threads: int = Option(4, help="Number of parallel threads for generating/posting.", callback=validate_positive),
    volume: int = Option(10000, help="Total number of play events to generate (historical) or events per minute (live).", callback=validate_positive),
    historical: bool = Option(False, help="Flag to enable historical mode."),
    live: bool = Option(False, help="Flag to enable live mode."),
    start_datetime: str = Option(None, help="Start ISO datetime for historical data.", callback=validate_datetime),
    end_datetime: str = Option(None, help="End ISO datetime for historical data.", callback=validate_datetime),
    posting_rate: float = Option(10.0, help="Max events per second to post to the API (historical mode).", callback=validate_positive),
    duration_seconds: int = Option(0, help="Duration for live simulation in seconds (0 = indefinite).", callback=validate_positive),
    format: str = Option("csv", help="Master data file format (csv or json).", callback=validate_format),
):
    """
    Run the data simulator in historical or live mode. (Implementation pending)
    """
    run_simulation_command(
        master_data_dir=master_data_dir,
        api_endpoint=api_endpoint,
        threads=threads,
        volume=volume,
        historical=historical,
        live=live,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        posting_rate=posting_rate,
        duration_seconds=duration_seconds,
        format=format,
    ) 