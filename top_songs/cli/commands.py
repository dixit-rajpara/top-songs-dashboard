"""
Command-line interface for the Top Songs Dashboard application.
"""
import asyncio
import sys
import typer
from rich.console import Console
from rich.table import Table
from top_songs.core.connectivity import (
    check_postgres_connection,
    check_kafka_connection,
    check_object_store_connection,
)

# Create Typer app
app = typer.Typer(
    name="top-songs",
    help="Top Songs Dashboard CLI",
    add_completion=False,
)

# Console for rich output
console = Console()

@app.command("check-connectivity")
def check_connectivity():
    """Check connectivity to all configured services."""
    console.print("\n[bold]Checking service connections...[/]\n")
    
    table = Table(show_header=True)
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="cyan")
    
    # Check Postgres
    pg_result = asyncio.run(check_postgres_connection())
    table.add_row(
        "PostgreSQL", 
        "[green]Connected[/]" if pg_result else "[red]Failed[/]"
    )
    
    # Check Kafka
    kafka_result = check_kafka_connection()
    table.add_row(
        "Kafka", 
        "[green]Connected[/]" if kafka_result else "[red]Failed[/]"
    )
    
    # Check Object Store (MinIO/S3)
    obj_store_result = check_object_store_connection()
    table.add_row(
        "Object Store (MinIO/S3)", 
        "[green]Connected[/]" if obj_store_result else "[red]Failed[/]"
    )
    
    console.print(table)
    console.print()
    
    # Return exit code based on all services connecting
    if not all([pg_result, kafka_result, obj_store_result]):
        sys.exit(1)

@app.command("about")
def about():
    """Display information about the application."""
    console.print("\n[bold]Top Songs Dashboard[/]\n")
    console.print("Version: 0.1.0")
    console.print("Author: Dixit Rajpara")
    console.print("Description: A dashboard for viewing top songs")

if __name__ == "__main__":
    app() 