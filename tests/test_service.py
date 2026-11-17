"""Unit tests for gradebook models, pure services, and calculations."""

import unittest

from gradebook import service
from gradebook.models import Course, Enrollment, Student
from gradebook.storage import empty_data


class TestModels(unittest.TestCase):
    def test_student_rejects_empty_name(self):
        with self.assertRaises(ValueError):
            Student(1, "   ")

    def test_course_normalizes_code(self):
        course = Course(" cs101 ", "Intro to CS")
        self.assertEqual(course.code, "CS101")

    def test_enrollment_rejects_out_of_range_grade(self):
        enrollment = Enrollment(1, "CS101")
        with self.assertRaises(ValueError):
            enrollment.add_grade(101)


class TestGradebookService(unittest.TestCase):
    def setUp(self):
        self.data = empty_data()

    def make_enrolled_student(self):
        data, student_id = service.add_student(self.data, "Ada Lovelace")
        data = service.add_course(data, "CS101", "Intro to CS")
        data = service.enroll(data, student_id, "CS101")
        return data, student_id

    def test_add_student_returns_new_data_and_id_without_mutation(self):
        updated, student_id = service.add_student(self.data, "Ada Lovelace")
        self.assertEqual(student_id, 1)
        self.assertEqual(updated["students"][0]["name"], "Ada Lovelace")
        self.assertEqual(self.data["students"], [])
        self.assertEqual(self.data["next_student_id"], 1)

    def test_add_course_rejects_duplicate_code(self):
        data = service.add_course(self.data, "CS101", "Intro")
        with self.assertRaises(ValueError):
            service.add_course(data, "cs101", "Duplicate")
        self.assertEqual(len(data["courses"]), 1)

    def test_enroll_and_reject_duplicate_enrollment(self):
        data, student_id = service.add_student(self.data, "Ada")
        data = service.add_course(data, "CS101", "Intro")
        enrolled = service.enroll(data, student_id, "CS101")
        with self.assertRaises(ValueError):
            service.enroll(enrolled, student_id, "CS101")
        self.assertEqual(len(data["enrollments"]), 0)

    def test_add_grade_and_compute_average(self):
        data, student_id = self.make_enrolled_student()
        data = service.add_grade(data, student_id, "CS101", 90)
        data = service.add_grade(data, student_id, "CS101", 100)
        self.assertEqual(service.compute_average(data, student_id, "CS101"), 95)

    def test_invalid_grade_is_rejected(self):
        data, student_id = self.make_enrolled_student()
        with self.assertRaises(ValueError):
            service.add_grade(data, student_id, "CS101", 120)

    def test_average_requires_enrollment(self):
        with self.assertRaises(ValueError):
            service.compute_average(self.data, 1, "CS101")

    def test_gpa_is_mean_of_course_averages(self):
        data, student_id = service.add_student(self.data, "Ada")
        data = service.add_course(data, "CS101", "Intro")
        data = service.add_course(data, "PY201", "Python")
        data = service.enroll(data, student_id, "CS101")
        data = service.enroll(data, student_id, "PY201")
        data = service.add_grade(data, student_id, "CS101", 80)
        data = service.add_grade(data, student_id, "PY201", 100)
        self.assertEqual(service.compute_gpa(data, student_id), 90)

    def test_list_sorting_does_not_change_input(self):
        data, _ = service.add_student(self.data, "Zoe")
        data, _ = service.add_student(data, "Ada")
        original = [item["name"] for item in data["students"]]
        result = service.list_students(data, "name")
        self.assertEqual([item["name"] for item in result], ["Ada", "Zoe"])
        self.assertEqual([item["name"] for item in data["students"]], original)


if __name__ == "__main__":
    unittest.main()
