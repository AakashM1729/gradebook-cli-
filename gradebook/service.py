"""Pure business-logic functions for gradebook records.

Each write operation returns a new data dictionary. The input dictionary and
its nested records are not modified.
"""

from .models import Course, Enrollment, Student


def parse_grade(value):
    """Convert a string to a float and validate the inclusive 0-100 range."""
    try:
        grade = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Grade must be numeric (0-100).") from exc
    if not 0 <= grade <= 100:
        raise ValueError("Grade must be between 0 and 100.")
    return grade


def _copy_data(data):
    """Copy the gradebook's mutable containers without changing the input."""
    return {
        "students": [dict(item) for item in data["students"]],
        "courses": [dict(item) for item in data["courses"]],
        "enrollments": [
            {**item, "grades": list(item["grades"])}
            for item in data["enrollments"]
        ],
        "next_student_id": data.get("next_student_id", 1),
    }


def add_student(data, name):
    """Return (updated_data, new_student_id) without mutating data."""
    student_id = int(data.get("next_student_id", 1))
    student = Student(student_id, name)
    updated = _copy_data(data)
    updated["students"].append({"id": student.id, "name": student.name})
    updated["next_student_id"] = student_id + 1
    return updated, student_id


def add_course(data, code, title):
    """Return updated data containing a new uniquely coded course."""
    course = Course(code, title)
    if any(item["code"].upper() == course.code for item in data["courses"]):
        raise ValueError(f"Course {course.code} already exists.")
    updated = _copy_data(data)
    updated["courses"].append({"code": course.code, "title": course.title})
    return updated


def enroll(data, student_id, course_code):
    """Return updated data after enrolling an existing student in a course."""
    course_code = course_code.strip().upper()
    if not any(item["id"] == student_id for item in data["students"]):
        raise ValueError(f"Student ID {student_id} does not exist.")
    if not any(item["code"].upper() == course_code for item in data["courses"]):
        raise ValueError(f"Course {course_code} does not exist.")
    if any(item["student_id"] == student_id and item["course_code"] == course_code
           for item in data["enrollments"]):
        raise ValueError("This student is already enrolled in that course.")
    Enrollment(student_id, course_code)
    updated = _copy_data(data)
    updated["enrollments"].append({
        "student_id": student_id,
        "course_code": course_code,
        "grades": [],
    })
    return updated


def add_grade(data, student_id, course_code, grade):
    """Return updated data with a validated grade added to an enrollment."""
    grade = parse_grade(grade)
    course_code = course_code.strip().upper()
    enrollment_index = next((index for index, item in enumerate(data["enrollments"])
                             if item["student_id"] == student_id
                             and item["course_code"] == course_code), None)
    if enrollment_index is None:
        raise ValueError("Student is not enrolled in that course.")
    updated = _copy_data(data)
    updated["enrollments"][enrollment_index]["grades"].append(grade)
    return updated


def list_students(data, sort="name"):
    """Return a new student list sorted by name or ID."""
    if sort not in ("name", "id"):
        raise ValueError("Students can be sorted by name or id.")
    return sorted((dict(item) for item in data["students"]),
                  key=lambda item: item[sort])


def list_courses(data, sort="code"):
    """Return a new course list sorted by code or title."""
    if sort not in ("code", "title"):
        raise ValueError("Courses can be sorted by code or title.")
    return sorted((dict(item) for item in data["courses"]),
                  key=lambda item: item[sort])


def list_enrollments(data, sort="name"):
    """Return enrollments sorted by student name or course code."""
    if sort not in ("name", "code"):
        raise ValueError("Enrollments can be sorted by name or code.")
    names = {item["id"]: item["name"] for item in data["students"]}
    records = [
        {**item, "grades": list(item["grades"])}
        for item in data["enrollments"]
    ]
    if sort == "name":
        return sorted(records, key=lambda item: (
            names.get(item["student_id"], ""), item["course_code"]
        ))
    return sorted(records, key=lambda item: (
        item["course_code"], names.get(item["student_id"], "")
    ))


def compute_average(data, student_id, course_code):
    """Return a student's average in one course, or None if there are no grades."""
    course_code = course_code.strip().upper()
    enrollment = next((item for item in data["enrollments"]
                       if item["student_id"] == student_id
                       and item["course_code"] == course_code), None)
    if enrollment is None:
        raise ValueError("Student is not enrolled in that course.")
    grades = enrollment["grades"]
    return sum(grades) / len(grades) if grades else None


def compute_gpa(data, student_id):
    """Return the mean of a student's course averages, or None without grades."""
    if not any(item["id"] == student_id for item in data["students"]):
        raise ValueError(f"Student ID {student_id} does not exist.")
    averages = [
        average
        for item in data["enrollments"]
        if item["student_id"] == student_id
        for average in [compute_average(data, student_id, item["course_code"])]
        if average is not None
    ]
    return sum(averages) / len(averages) if averages else None
