from __future__ import annotations

from app.models import Student
from app.repositories import CourseRepository, EnrollmentRepository, StudentRepository
from app.utils import select


class ReportService:
    def __init__(
        self,
        student_repository: StudentRepository,
        course_repository: CourseRepository,
        enrollment_repository: EnrollmentRepository,
    ):
        self.student_repository = student_repository
        self.course_repository = course_repository
        self.enrollment_repository = enrollment_repository

    def average(self, grades: list[float]) -> float:
        return sum(grades) / len(grades) if grades else 0.0

    def student_average(self, student_no: str) -> float:
        student = self.student_repository.get_by_number(student_no.strip())
        if student is None:
            return 0.0
        grades = [
            e.grade
            for e in self.enrollment_repository.by_student(student.id)
            if e.grade is not None
        ]
        return self.average(grades)

    def top_students(self, limit: int = 3) -> list[tuple[Student, float]]:
        rows = [
            (s, self.student_average(s.student_no))
            for s in self.student_repository.list()
        ]
        return sorted(rows, key=lambda row: row[1], reverse=True)[:limit]

    def qualified_students(self, minimum: float = 60) -> list[Student]:
        return select(
            self.student_repository.list(),
            lambda s: self.student_average(s.student_no) >= minimum,
        )
