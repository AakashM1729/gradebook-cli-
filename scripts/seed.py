"""Create sample gradebook records for demonstration and testing."""

from gradebook import service
from gradebook.storage import empty_data, save_data


def main():
    """Create and save three students, two courses, and sample grades."""
    data = empty_data()
    data, ada = service.add_student(data, "Ada Lovelace")
    data, alan = service.add_student(data, "Alan Turing")
    data, grace = service.add_student(data, "Grace Hopper")
    data = service.add_course(data, "CS101", "Introduction to Computer Science")
    data = service.add_course(data, "PY201", "Python Programming")

    for student_id, course_code in (
        (ada, "CS101"), (ada, "PY201"), (alan, "CS101"),
        (alan, "PY201"), (grace, "PY201"),
    ):
        data = service.enroll(data, student_id, course_code)

    for student_id, course_code, grade in (
        (ada, "CS101", 95), (ada, "CS101", 88), (ada, "PY201", 97),
        (alan, "CS101", 84), (alan, "PY201", 91), (grace, "PY201", 99),
    ):
        data = service.add_grade(data, student_id, course_code, grade)

    save_data(data)
    print("Sample gradebook saved to data/gradebook.json")


if __name__ == "__main__":
    main()
