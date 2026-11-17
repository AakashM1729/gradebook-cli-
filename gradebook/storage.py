"""JSON persistence and logging helpers for the gradebook."""

import json
import logging
from pathlib import Path

DEFAULT_PATH = Path("data/gradebook.json")
LOG_PATH = Path("logs/app.log")


def configure_logging():
    """Configure INFO and ERROR logging in logs/app.log."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        force=True,
    )


def empty_data():
    """Return a new empty gradebook data structure."""
    return {"students": [], "courses": [], "enrollments": [], "next_student_id": 1}


def load_data(path=DEFAULT_PATH):
    """Load JSON data; use an empty gradebook if the file does not exist."""
    configure_logging()
    file_path = Path(path)
    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("Invalid gradebook file: top level must be an object.")
        for key in ("students", "courses", "enrollments"):
            if key not in data or not isinstance(data[key], list):
                raise ValueError(f"Invalid gradebook file: '{key}' must be a list.")
        data.setdefault("next_student_id", 1)
        logging.info("Loaded gradebook data from %s", file_path)
        return data
    except FileNotFoundError:
        logging.info("No data file at %s; starting with an empty gradebook", file_path)
        return empty_data()
    except json.JSONDecodeError as exc:
        logging.error("Invalid JSON in %s: %s", file_path, exc)
        raise ValueError(
            f"Could not read {file_path}: invalid JSON. Check the file syntax."
        ) from exc
    except OSError as exc:
        logging.exception("Could not load %s", file_path)
        raise ValueError(f"Could not load data: {exc}") from exc


def save_data(data, path=DEFAULT_PATH):
    """Save gradebook data as formatted JSON, creating its parent directory."""
    configure_logging()
    file_path = Path(path)
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        logging.info("Saved gradebook data to %s", file_path)
    except OSError as exc:
        logging.exception("Could not save %s", file_path)
        raise ValueError(f"Could not save data: {exc}") from exc
