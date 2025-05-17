# 🎼 Data Simulator - Detailed Plan

## 1. Introduction & Purpose

This document outlines the detailed plan for creating a data simulator for the Top Songs Dashboard project. The simulator will generate synthetic song play data, which can be used to test the ingestion pipeline and downstream processing components. It will be configurable to produce both master data (songs, users, locations) and transactional play event data. The simulator will be invokable via a CLI.

## 2. Key Requirements & Features

*   **Core Libraries**: Utilize `Faker` for generating realistic-looking fake data and `Simpy` for event-based simulation, particularly for the live mode.
*   **CLI Invocation**: The simulator will be accessible and configurable through a `Typer`-based command-line interface.
*   **Master Data Generation**:
    *   A dedicated CLI command to generate master data (songs, users, locations).
    *   Option to specify the number of records for each master data entity (e.g., 1000 songs, 5000 users, 100 regions).
    *   Master data will be stored in a specified output directory, defaulting to `data/master/` within the project root (e.g., `data/master/songs.csv`, `data/master/users.json`). The format (CSV, JSON) should be decided during implementation, prioritizing ease of use.
*   **Transactional Data Simulation (Play Events)**:
    *   A dedicated CLI command to simulate and post transactional song play data.
    *   **Modes of Operation**:
        *   **Historical Mode**:
            *   Accepts `start_datetime` and `end_datetime` parameters to define the period for data generation.
            *   Accepts a `rate` parameter (e.g., events per second) to control the speed at which historical data is posted to the API endpoint, preventing server overload.
        *   **Live Mode**:
            *   Emulates real-time clients generating a continuous stream of play events.
            *   May include a parameter for simulation duration or run indefinitely until interrupted.
    *   **Common Parameters (for both modes)**:
        *   `volume`: Specifies the amount of data to generate (e.g., total number of play events for historical, or events per time unit for live).
        *   `threads`: Number of concurrent threads/processes to use for generating and posting data to enhance throughput.
*   **Data Integrity**:
    *   Transactional play events **must** use IDs (song ID, user ID, location ID) from the generated/existing master data.
    *   The simulator must check for the existence of master data before starting transactional data generation. If master data is not found, it should raise an error and instruct the user to generate it first.
*   **Data Models**: All data schemas (Pydantic models) for master data entities and play events will be defined in the `top_songs/core/models/` directory.
*   **Sensible Defaults**: All CLI options should have reasonable default values.
*   **Existing Interfaces**: The simulator will utilize existing interfaces for posting data (e.g., an HTTP client to post to the FastAPI server's `/play` endpoint). No new interface classes for storage or streaming are expected to be built *for the simulator itself*, beyond what's needed to write master data to files.

## 3. CLI Design (Typer-based)

The simulator commands will be integrated into the existing main CLI application defined in `top_songs.cli.commands.py`. A new subcommand group `simulate` will be added to the main `app` to house the simulator-specific commands.

Example Invocation:
```
top-songs simulate --help
top-songs simulate generate-master [OPTIONS]
top-songs simulate run [OPTIONS]
```

### 3.1. Subcommand Group: `simulate`

This command group will be registered with the main `Typer` app in `top_songs.cli.commands.py`.
The logic for these commands will reside primarily in `top_songs.ingestion.simulator.*` modules.

### 3.2. Command: `generate-master`

For generating master data.

```
top-songs simulate generate-master [OPTIONS]
```

**Options**:
*   `--output-dir TEXT`: Directory to store master data files. (Default: `data/master/`)
*   `--num-songs INTEGER`: Number of song records to generate. (Default: 1000)
*   `--num-users INTEGER`: Number of user records to generate. (Default: 5000)
*   `--num-locations INTEGER`: Number of location/region records to generate. (Default: 100)
*   `--format TEXT`: Output format for master data (e.g., `csv`, `json`). (Default: `csv`)

### 3.3. Command: `run`

For generating and posting transactional song play data.

```
top-songs simulate run [OPTIONS]
```

**Options**:
*   **Mode Selection (mutually exclusive group)**:
    *   `--historical`: Flag to enable historical mode.
    *   `--live`: Flag to enable live mode. (Default if no mode specified, or make one mandatory)
*   **Historical Mode Parameters**:
    *   `--start-datetime TEXT`: Start ISO datetime for historical data (e.g., "2023-01-01T00:00:00"). Required if `--historical`.
    *   `--end-datetime TEXT`: End ISO datetime for historical data (e.g., "2023-01-31T23:59:59"). Required if `--historical`.
    *   `--posting-rate FLOAT`: Max events per second to post to the API. (Default: 10.0)
*   **Live Mode Parameters**:
    *   `--duration-seconds INTEGER`: For how long the live simulation should run. If 0 or not provided, runs indefinitely. (Default: 0)
*   **Common Parameters**:
    *   `--master-data-dir TEXT`: Directory to load master data from. (Default: `data/master/`)
    *   `--volume INTEGER`: Total number of play events to generate (for historical) or target events per minute (for live). (Default: 10000 for historical, 60 for live)
    *   `--threads INTEGER`: Number of parallel threads for generating/posting. (Default: 4)
    *   `--api-endpoint TEXT`: The URL of the API endpoint to post play events. (Default: `http://localhost:8000/play`)

## 4. Data Models (`top_songs/core/models/`)

Pydantic models will be defined for:

*   **`SongMasterData`**:
    *   `song_id: str` (UUID)
    *   `title: str`
    *   `artist_name: str`
    *   `album_name: str`
    *   `genre: str`
    *   `duration_ms: int`
    *   `release_date: date`
*   **`UserMasterData`**:
    *   `user_id: str` (UUID)
    *   `username: str`
    *   `email: str`
    *   `registration_date: date`
    *   `country: str`
*   **`LocationMasterData`** (or `RegionMasterData`):
    *   `location_id: str` (UUID or a composite key if hierarchical, e.g. country_code + city_name)
    *   `city: str`
    *   `country_code: str` (e.g., "US", "GB")
    *   `latitude: float`
    *   `longitude: float`
*   **`PlayEventData`** (Transactional Data, sent to API):
    *   `event_id: str` (UUID, generated per event)
    *   `song_id: str` (FK to `SongMasterData.song_id`)
    *   `user_id: str` (FK to `UserMasterData.user_id`)
    *   `location_id: str` (FK to `LocationMasterData.location_id`)
    *   `played_at: datetime` (Timestamp of when the song was played)
    *   `play_duration_ms: int` (Actual duration the user listened, can be <= `SongMasterData.duration_ms`)
    *   `device_type: str` (e.g., "mobile", "desktop", "tablet")

## 5. Master Data Generation Logic (`top_songs.ingestion.simulator.master_data_generator`)

*   Uses `Faker` to generate attributes for `SongMasterData`, `UserMasterData`, `LocationMasterData`.
*   Ensures unique IDs for each record within its type.
*   Writes the generated data to the specified `--output-dir` in the chosen `--format` (e.g., CSV files: `songs.csv`, `users.csv`, `locations.csv`).
*   File structure example:
    ```
    data/
    └── master/
        ├── songs.csv
        ├── users.csv
        └── locations.csv
    ```

## 6. Transactional Data Simulation Logic (`top_songs.ingestion.simulator.event_simulator`)

### 6.1. Core Components:
*   **Master Data Loader**: Reads master data from files into memory (e.g., lists of Pydantic objects or pandas DataFrames) for quick lookups.
*   **Event Factory**: Creates `PlayEventData` instances.
    *   Randomly selects `song_id`, `user_id`, `location_id` from loaded master data.
    *   Generates `played_at` timestamp based on the simulation mode (historical range or current time for live).
    *   Generates realistic `play_duration_ms` (e.g., a random percentage of the song's total duration).
    *   Uses `Faker` for other fields like `device_type`.
*   **Simulation Engine (Simpy for Live Mode)**:
    *   For Live mode, `Simpy` can be used to model user behaviors and event timings. Each "user" or "session" could be a Simpy process.
    *   For Historical mode, Simpy might be less critical, and a loop with controlled timing (based on `--posting-rate`) could suffice. However, Simpy could still manage event generation over the historical timeline.
*   **API Poster**:
    *   A component responsible for sending the `PlayEventData` (serialized to JSON) to the configured `--api-endpoint`.
    *   Handles concurrency using `threading` or `asyncio` (if API client supports it) based on the `--threads` parameter.
    *   Implements rate limiting for historical data posting.

### 6.2. Historical Mode:
1.  Load master data.
2.  Validate `start_datetime` and `end_datetime`.
3.  Calculate the total number of events to generate (`--volume`).
4.  Iterate to generate events:
    *   For each event, assign a `played_at` timestamp distributed within the `[start_datetime, end_datetime]` range.
    *   Post events to the API, respecting the `--posting-rate`. This might involve calculating sleep times between posts or batches of posts.
    *   Use multiple threads if `--threads` > 1.

### 6.3. Live Mode:
1.  Load master data.
2.  Initialize `Simpy` environment if used, or set up a continuous generation loop.
3.  Generate events at a rate implied by `--volume` (e.g., if volume is events/minute).
    *   `played_at` should be current time or slightly in the past.
    *   Simulate a stream of events.
    *   Use multiple threads for generation and posting.
4.  Run for `--duration-seconds` or indefinitely.

## 7. Error Handling and Validation

*   **Master Data**:
    *   Check if master data directory and files exist before `run` command. If not, exit with a clear error message guiding the user to run `generate-master`.
*   **CLI Parameters**:
    *   `Typer` will handle basic type validation.
    *   Custom validation for datetime formats, ranges, and interdependent options (e.g., historical mode requiring start/end dates).
*   **API Posting**:
    *   Handle potential HTTP errors (e.g., 4xx, 5xx) from the API. Log errors and decide on retry strategy or graceful failure.

## 8. Dependencies

*   `typer`: For CLI.
*   `faker`: For generating fake data.
*   `simpy`: For event-based simulation (primarily for live mode).
*   `pydantic`: For data models and validation.
*   `httpx` or `requests`: For making HTTP calls to the API server (to be chosen during implementation).
*   (Potentially `pandas` for easier master data handling if CSV is chosen and data size is manageable).

## 9. Proposed Directory Structure (within `top_songs/ingestion/simulator/`)

```
top_songs/
├── core/
│   └── models/
│       ├── __init__.py
│       └── simulator_models.py  # Or individual files like song_model.py, user_model.py
├── ingestion/
│   └── simulator/
│       ├── __init__.py
│       ├── cli.py                     # Main Typer app and command definitions
│       ├── master_data_generator.py   # Logic for generating master data
│       ├── event_factory.py           # Creates PlayEventData instances
│       ├── simulation_engine.py       # Core simulation logic (Simpy or custom loops)
│       ├── api_poster.py              # Handles posting data to the API
│       └── utils.py                   # Helper functions, constants
└── ... (other project files)
```

## 10. Task Breakdown / Implementation Steps (High-Level)

The following is a general sequence of steps. Refer to Section 11 for a more detailed checklist.

1.  **Setup & Configuration**:
    *   Add `Faker`, `Simpy`, `Typer`, `httpx` (or `requests`) to `pyproject.toml`.
    *   Create the directory structure under `top_songs/ingestion/simulator/` and `top_songs/core/models/`.
2.  **Data Models**:
    *   Define Pydantic models (`SongMasterData`, `UserMasterData`, `LocationMasterData`, `PlayEventData`) in `top_songs/core/models/simulator_models.py`.
3.  **CLI Integration**:
    *   Create `top_songs/ingestion/simulator/cli.py` to define the `Typer` app for the `simulate` subcommand group and its commands (`generate-master`, `run`).
    *   Register the `simulate` subcommand group in `top_songs/cli/commands.py`.
4.  **Master Data Generation**:
    *   Implement `master_data_generator.py` using `Faker`.
    *   Implement the `generate-master` CLI command in `cli.py`.
    *   Allow configurable output formats (CSV as default).
    *   Implement the `generate-master` command logic in `top_songs.ingestion.simulator.commands` (or a dedicated module), linking it to the CLI definition.
5.  **Core Simulation Components**:
    *   Implement `event_factory.py` to create `PlayEventData` instances using loaded master data.
    *   Implement `api_poster.py` with basic HTTP posting capabilities.
6.  **Historical Mode Simulation**:
    *   Implement the historical mode logic in `top_songs.ingestion.simulator.simulation_engine`.
    *   Integrate with `api_poster.py`, including rate limiting.
    *   Connect this logic to the `run` command's historical mode options.
7.  **Live Mode Simulation**:
    *   Implement the live mode logic in `top_songs.ingestion.simulator.simulation_engine`, potentially using `Simpy`.
    *   Integrate with `api_poster.py`.
    *   Connect this logic to the `run` command's live mode options.
8.  **Concurrency**:
    *   Modify `APIPoster` and the calling logic in `run_simulation_command` to use `threading` (or `asyncio` with `httpx.AsyncClient`) for concurrent API calls, based on `--threads`.
    *   Ensure thread-safety if shared resources are accessed (e.g., master data lists).
9.  **Error Handling & Validation**:
    *   Add robust error handling (master data checks, API errors).
    *   Add input validation for CLI parameters.
10. **Defaults & Refinements**:
    *   Ensure all options have sensible defaults.
    *   Refine logging and user feedback.
11. **Documentation**:
    *   Add docstrings to all functions and classes.
    *   Update `README.md` with instructions on how to use the simulator.
12. **Unit Tests**:
    *   Write Pytest unit tests for:
        *   Master data generation (correct number of records, file creation).
        *   Event factory (correct structure of `PlayEventData`).
        *   CLI command parsing and option validation.
        *   (Mocked) API poster functionality.

## 11. Detailed Task Checklist

**Phase 1.0: Setup and Basic Structure**
- [x] **Dependencies**: Add `Faker`, `Simpy`, `httpx` (or `requests`) to `pyproject.toml` under `dependencies`.
- [x] **Directory Structure**: Create `top_songs/ingestion/simulator/`.
- [x] **Core Models Directory**: Ensure `top_songs/core/models/` exists.
- [x] **Basic CLI Files**:
    - [x] Create `top_songs/ingestion/simulator/__init__.py`.
    - [x] Create `top_songs/ingestion/simulator/cli.py` (will hold Typer app for `simulate` subcommand).
    - [x] Create `top_songs/ingestion/simulator/commands.py` (will hold implementations for CLI commands).
    - [x] Create `top_songs/ingestion/simulator/utils.py`.

**Phase 1.1: Data Models**
- [x] Create `top_songs/core/models/__init__.py` if it doesn't exist.
- [x] Create `top_songs/core/models/simulator_models.py`.
- [x] Define `SongMasterData` (Pydantic model) in `simulator_models.py`.
- [x] Define `UserMasterData` (Pydantic model) in `simulator_models.py`.
- [x] Define `LocationMasterData` (Pydantic model) in `simulator_models.py`.
- [x] Define `PlayEventData` (Pydantic model) in `simulator_models.py`.
- [x] Add `__init__.py` exports in `top_songs/core/models/__init__.py` for easy importing.

**Phase 1.2: CLI Integration**
- [x] In `top_songs/ingestion/simulator/cli.py`:
    - [x] Define a new `Typer` app (e.g., `simulator_app = typer.Typer(name="simulate", help="Generate and simulate song play data.")`).
- [x] In `top_songs/cli/commands.py`:
    - [x] Import `simulator_app` from `top_songs.ingestion.simulator.cli`.
    - [x] Add `simulator_app` as a subcommand to the main `app` (e.g., `app.add_typer(simulator_app)`).
- [x] Test basic CLI integration (e.g., `top-songs simulate --help`).

**Phase 1.3: Master Data Generation**
- [x] Create `top_songs/ingestion/simulator/master_data_generator.py`.
- [x] Implement function(s) in `master_data_generator.py` to:
    - [x] Generate `SongMasterData` instances using `Faker`.
    - [x] Generate `UserMasterData` instances using `Faker`.
    - [x] Generate `LocationMasterData` instances using `Faker`.
    - [x] Ensure unique IDs for each master data type.
- [x] Implement logic to write master data to files (e.g., CSV or JSON) in a specified output directory.
    - [x] Handle `csv` format.
    - [x] Handle `json` format (optional, if time permits or deemed useful).
- [x] In `top_songs/ingestion/simulator/commands.py`:
    - [x] Implement the `generate_master_data_command` function.
- [x] In `top_songs/ingestion/simulator/cli.py`:
    - [x] Define the `generate-master` command, linking it to `generate_master_data_command`.
    - [x] Add options: `--output-dir`, `--num-songs`, `--num-users`, `--num-locations`, `--format`.
    - [x] Implement sensible defaults for options.
- [x] Test `top-songs simulate generate-master` command.

**Phase 1.4: Core Simulation Components**
- [x] Create `top_songs/ingestion/simulator/event_factory.py`.
- [x] Implement `EventFactory` class or functions in `event_factory.py`:
    - [x] Method to load master data from files (from `--master-data-dir`).
    - [x] Method to create `PlayEventData` instances:
        - [x] Randomly select IDs from loaded master data.
        - [x] Generate `played_at` timestamp.
        - [x] Generate `play_duration_ms`.
        - [x] Use `Faker` for `device_type`.
- [x] Create `top_songs/ingestion/simulator/api_poster.py`.
- [x] Implement `APIPoster` class in `api_poster.py`:
    - [x] Constructor to take API endpoint URL.
    - [x] Method to post single `PlayEventData` (serialized to JSON) using `httpx` or `requests`.
    - [x] Basic error handling for HTTP requests.

**Phase 1.5: Transactional Data Simulation - `run` command structure**
- [x] In `top_songs/ingestion/simulator/commands.py`:
    - [x] Implement the `run_simulation_command` function (placeholder initially).
- [x] In `top_songs/ingestion/simulator/cli.py`:
    - [x] Define the `run` command, linking to `run_simulation_command`.
    - [x] Add common options: `--master-data-dir`, `--api-endpoint`, `--threads`, `--volume`.
    - [x] Add mode flags: `--historical`, `--live`.
    - [x] Add historical options: `--start-datetime`, `--end-datetime`, `--posting-rate`.
    - [x] Add live options: `--duration-seconds`.
    - [x] Implement sensible defaults.
- [x] Implement validation: Check for master data existence before proceeding. Raise error if not found. (To be implemented in later phases)

**Phase 1.6: Historical Mode Implementation**
- [x] Create `top_songs/ingestion/simulator/simulation_engine.py`.
- [x] Implement historical mode logic within `simulation_engine.py`:
    - [x] Function to generate a list of `PlayEventData` for the specified period and volume.
    - [x] Distribute `played_at` timestamps within the historical range.
- [x] In `top_songs/ingestion/simulator/commands.py` (for `run_simulation_command`):
    - [x] Integrate historical mode logic.
    - [x] Use `APIPoster` to send data, respecting `--posting-rate` (implement delay/sleep). (To be implemented in next phase)
- [x] Test historical mode: `top-songs simulate run --historical ...` (To be implemented in next phase)

**Phase 1.7: Live Mode Implementation**
- [x] Implement live mode logic within `simulation_engine.py`:
    - [x] Use `simpy` if deemed beneficial for managing event timing and processes.
    - [x] Alternatively, use a timed loop for continuous generation.
    - [x] Generate `played_at` as current time.
    - [x] Generate events based on `--volume` (events per unit of time).
- [x] In `top_songs/ingestion/simulator/commands.py` (for `run_simulation_command`):
    - [x] Integrate live mode logic.
    - [x] Use `APIPoster` to send data.
    - [x] Respect `--duration-seconds`.
- [x] Test live mode: `top-songs simulate run --live ...`.

**Phase 1.8: Concurrency**
- [x] Modify `APIPoster` and the calling logic in `run_simulation_command` to use `threading` (or `asyncio` with `httpx.AsyncClient`) for concurrent API calls, based on `--threads`.
- [x] Ensure thread-safety if shared resources are accessed (e.g., master data lists).

**Phase 1.9: Error Handling, Validation & Refinements**
- [x] Enhance CLI parameter validation in `top_songs/ingestion/simulator/cli.py` (e.g., datetime formats, positive integers).
- [x] Improve error handling in `APIPoster` (retries, logging).
- [x] Add comprehensive logging throughout the simulator modules.
- [x] Ensure all CLI options have robust help messages and defaults are clear.

**Phase 2.0: Documentation & Testing**
- [x] Write Google-style docstrings for all new functions and classes.
- [x] Update project `README.md` with instructions on how to use the data simulator CLI commands.
- [x] Write Pytest unit tests in `tests/ingestion/simulator/`:
    - [x] `test_master_data_generator.py`: Test master data creation, file output.
    - [x] `test_event_factory.py`: Test `PlayEventData` creation.
    - [x] `test_cli.py`: Test CLI command parsing, option validation (using `CliRunner` or similar).
    - [x] `test_api_poster.py`: Test API posting logic (mocking HTTP calls).
    - [x] `test_simulation_engine.py`: Test historical and live simulation logic (may require some mocking).