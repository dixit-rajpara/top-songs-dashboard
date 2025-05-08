"""
Command-line interface for the Top Songs Dashboard application.
"""
import asyncio
import sys
import typer
from rich.console import Console
from rich.table import Table
from confluent_kafka.admin import AdminClient

from top_songs.core.config import settings
from top_songs.storage.database.postgres import PostgresInterface
from top_songs.storage.object_store.s3 import ObjectStoreInterface

# Create Typer app
app = typer.Typer(
    name="top-songs",
    help="Top Songs Dashboard CLI",
    add_completion=False,
)

# Console for rich output
console = Console()


async def check_postgres_connection() -> bool:
    """Check if PostgreSQL connection is working."""
    if settings.postgres is None:
        console.print("[yellow]PostgreSQL settings not configured[/]")
        return False
    
    pg = PostgresInterface()
    try:
        await pg.connect()
        await pg.disconnect()
        return True
    except Exception as e:
        console.print(f"[red]PostgreSQL connection error: {str(e)}[/]")
        return False


def check_kafka_connection() -> bool:
    """Check if Kafka connection is working."""
    try:
        # Create Kafka admin client to check the connection
        conf = {'bootstrap.servers': settings.kafka.bootstrap_servers}
        admin_client = AdminClient(conf)
        
        # Get metadata to check connection
        _ = admin_client.list_topics(timeout=5)
        return True
    except Exception as e:
        console.print(f"[red]Kafka connection error: {str(e)}[/]")
        return False


def check_object_store_connection() -> bool:
    """Check if Object Store (MinIO/S3) connection is working."""
    if settings.object_store is None:
        console.print("[yellow]Object Store settings not configured[/]")
        return False
    
    try:
        obj_store = ObjectStoreInterface()
        # Check connection by listing buckets
        obj_store.client.list_buckets()
        return True
    except Exception as e:
        console.print(f"[red]Object Store connection error: {str(e)}[/]")
        return False


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