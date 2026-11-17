"""Data models and validation for the gradebook application."""


class Student:
    """Represent a student with a positive integer ID and a non-empty name."""

    def __init__(self, student_id: int, name: str):
        if isinstance(student_id, bool) or not isinstance(student_id, int) or student_id < 1:
            raise ValueError("Student ID must be a positive integer.")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Student name cannot be empty.")
        self.id = student_id
        self.name = name.strip()

    def __str__(self) -> str:
        return f"Student #{self.id}: {self.name}"


class Course:
    """Represent a course with a code and title."""

    def __init__(self, code: str, title: str):
        if not isinstance(code, str) or not code.strip():
            raise ValueError("Course code cannot be empty.")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Course title cannot be empty.")
        self.code = code.strip().upper()
        self.title = title.strip()

    def __str__(self) -> str:
        return f"{self.code}: {self.title}"


class Enrollment:
    """Represent one student's enrollment in a course and its grades."""

    def __init__(self, student_id: int, course_code: str, grades=None):
        if isinstance(student_id, bool) or not isinstance(student_id, int) or student_id < 1:
            raise ValueError("Student ID must be a positive integer.")
        if not isinstance(course_code, str) or not course_code.strip():
            raise ValueError("Course code cannot be empty.")
        self.student_id = student_id
        self.course_code = course_code.strip().upper()
        self.grades = []
        for grade in grades or []:
            self.add_grade(grade)

    def add_grade(self, grade) -> None:
        """Append a numeric grade in the inclusive range 0 to 100."""
        if isinstance(grade, bool) or not isinstance(grade, (int, float)):
            raise ValueError("Grade must be a number from 0 to 100.")
        if not 0 <= grade <= 100:
            raise ValueError("Grade must be between 0 and 100.")
        self.grades.append(float(grade))

    def __str__(self) -> str:
        return (f"Enrollment: student {self.student_id} in "
                f"{self.course_code} ({len(self.grades)} grades)")
