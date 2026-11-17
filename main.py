"""Command-line interface for the student gradebook."""

import argparse
import logging

from gradebook import service
from gradebook.storage import load_data, save_data


def build_parser():
    """Build the exact supported command and argument interface."""
    parser = argparse.ArgumentParser(description="Manage a student gradebook.")
    commands = parser.add_subparsers(dest="command", required=True)

    student = commands.add_parser("add-student", help="Add a student")
    student.add_argument("--name", required=True)

    course = commands.add_parser("add-course", help="Add a course")
    course.add_argument("--code", required=True)
    course.add_argument("--title", required=True)

    enrollment = commands.add_parser("enroll", help="Enroll a student in a course")
    enrollment.add_argument("--student-id", type=int, required=True)
    enrollment.add_argument("--course", required=True)

    grade = commands.add_parser("add-grade", help="Record a student's grade")
    grade.add_argument("--student-id", type=int, required=True)
    grade.add_argument("--course", required=True)
    grade.add_argument("--grade", type=service.parse_grade, required=True)

    listing = commands.add_parser("list", help="List gradebook records")
    listing.add_argument("kind", choices=("students", "courses", "enrollments"))
    listing.add_argument("--sort", choices=("name", "code"))

    average = commands.add_parser("avg", help="Calculate a course average")
    average.add_argument("--student-id", type=int, required=True)
    average.add_argument("--course", required=True)

    gpa = commands.add_parser("gpa", help="Calculate a student's GPA")
    gpa.add_argument("--student-id", type=int, required=True)
    return parser


def run(args):
    """Execute a parsed command and persist changes when needed."""
    data = load_data()

    if args.command == "add-student":
        data, student_id = service.add_student(data, args.name)
        save_data(data)
        print(f"Added student '{args.name.strip()}' with ID {student_id}.")
    elif args.command == "add-course":
        data = service.add_course(data, args.code, args.title)
        save_data(data)
        print(f"Added course {args.code.strip().upper()}.")
    elif args.command == "enroll":
        data = service.enroll(data, args.student_id, args.course)
        save_data(data)
        print(f"Enrolled student {args.student_id} in {args.course.strip().upper()}.")
    elif args.command == "add-grade":
        data = service.add_grade(data, args.student_id, args.course, args.grade)
        save_data(data)
        print(f"Recorded grade {args.grade:g}.")
    elif args.command == "list":
        if args.kind == "students":
            if args.sort not in (None, "name"):
                raise ValueError("Students can only be sorted by name.")
            for item in service.list_students(data, "name"):
                print(f"{item['id']}: {item['name']}")
        elif args.kind == "courses":
            if args.sort not in (None, "code"):
                raise ValueError("Courses can only be sorted by code.")
            for item in service.list_courses(data, "code"):
                print(f"{item['code']}: {item['title']}")
        else:
            for item in service.list_enrollments(data, args.sort or "name"):
                print(f"Student {item['student_id']} - {item['course_code']}: "
                      f"{item['grades']}")
    elif args.command == "avg":
        result = service.compute_average(data, args.student_id, args.course)
        print("No grades recorded yet." if result is None else f"Average: {result:.2f}")
    elif args.command == "gpa":
        result = service.compute_gpa(data, args.student_id)
        print("No course grades recorded yet." if result is None
              else f"GPA (mean percentage): {result:.2f}")


def main():
    """Parse command-line arguments and report friendly application errors."""
    parser = build_parser()
    args = parser.parse_args()
    try:
        run(args)
    except (ValueError, OSError) as exc:
        logging.exception("Command failed")
        print(f"Error: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
