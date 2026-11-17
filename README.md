# Gradebook CLI

A Python command-line application for managing students, courses, enrollments, and grades.

## Project structure

```text
gradebook-project/
├── data/gradebook.json       # Persistent JSON data (created when saved)
├── gradebook/
│   ├── __init__.py
│   ├── models.py             # Student, Course, Enrollment
│   ├── storage.py            # JSON load/save and logging
│   └── service.py            # Pure gradebook business functions
├── logs/app.log              # Application log (created automatically)
├── scripts/seed.py           # Sample-data generator
├── tests/test_service.py     # Unit tests
├── main.py                   # argparse command-line interface
└── README.md
```

## Requirements

- Python 3.9 or newer
- No third-party packages are required

## Setup (Windows PowerShell)

Run these commands from the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## Create sample data

```powershell
python -m scripts.seed
```

This writes three students, two courses, enrollments, and grades to `data/gradebook.json`.

## CLI commands

```powershell
python main.py add-student --name "Katherine Johnson"
python main.py add-course --code CS101 --title "Introduction to Computer Science"
python main.py enroll --student-id 1 --course CS101
python main.py add-grade --student-id 1 --course CS101 --grade 95
python main.py list students --sort name
python main.py list courses --sort code
python main.py list enrollments
python main.py avg --student-id 1 --course CS101
python main.py gpa --student-id 1
```

The `list` command supports `students`, `courses`, and `enrollments`. Student records are sorted by name; course records are sorted by code. Enrollment records can be sorted by student name or course code with `--sort name` or `--sort code`.

Example output:

```text
Added student 'Katherine Johnson' with ID 4.
Average: 91.50
GPA (mean percentage): 93.25
```

IDs and calculated values depend on the saved data.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## Data, validation, and logging

- JSON data is stored at `data/gradebook.json` by default.
- If the JSON file is missing, the application starts with an empty gradebook.
- Malformed JSON and file errors are reported instead of silently overwriting data.
- Student names, course codes, and course titles must be non-empty strings.
- Course codes are normalized to uppercase and must be unique.
- Grades must be numeric values from 0 through 100, inclusive.
- A student must exist and be enrolled before a grade can be recorded.
- INFO and ERROR events are written to `logs/app.log`.

## Design notes

- Service write functions are pure: they return updated data rather than modifying the input dictionary.
- `avg` returns the arithmetic mean of a student's grades in one course.
- `gpa` is the arithmetic mean of that student's course averages (percentage scale; not a credit-weighted 4.0 GPA).
- An empty grade list has no average; the CLI reports that no grades have been recorded.
